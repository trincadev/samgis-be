import json
import os
from collections.abc import Callable
from pathlib import Path

import structlog.stdlib
import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from samgis_core.utilities import create_folders_if_not_exists
from samgis_web.utilities import frontend_builder
from samgis_core.utilities.session_logger import setup_logging
from samgis_web.prediction_api.predictors import samexporter_predict
from samgis_web.utilities.type_hints import ApiRequestBody
from starlette.responses import JSONResponse, Response


load_dotenv()
project_root_folder = Path(globals().get("__file__", "./_")).absolute().parent
workdir = os.getenv("WORKDIR", project_root_folder)


def resolve_model_folder() -> Path:
    """Resolve model directory: MODEL_FOLDER env → registry default."""
    from samgis_core.prediction_api.model_registry import get_model_dir

    env_override = os.getenv("MODEL_FOLDER")
    if env_override is not None:
        return Path(env_override)
    variant = os.getenv("MODEL_VARIANT", "sam2.1_hiera_base_plus_uint8")
    return get_model_dir(variant)


model_folder = resolve_model_folder()

log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)
app_logger = structlog.stdlib.get_logger()
app_logger.info(f"PROJECT_ROOT_FOLDER:{project_root_folder}, WORKDIR:{workdir}.")
app_logger.info(f"model_folder resolved to: '{model_folder}'.")

folders_map = os.getenv("FOLDERS_MAP", "{}")
markdown_text = os.getenv("MARKDOWN_TEXT", "")
examples_text_list = os.getenv("EXAMPLES_TEXT_LIST", "").split("\n")
example_body = json.loads(os.getenv("EXAMPLE_BODY", "{}"))

static_dist_folder = Path(project_root_folder) / "static" / "dist"
input_css_path = os.getenv("INPUT_CSS_PATH", "src/input.css")
vite_index_url = os.getenv("VITE_INDEX_URL", "/")
vite_samgis_url = os.getenv("VITE_SAMGIS_URL", "/samgis")
fastapi_title = "samgis"
app = FastAPI(title=fastapi_title, version="1.0")


@app.middleware("http")
async def request_middleware(request: Request, call_next: Callable) -> Response:
    from samgis_web.web.middlewares import logging_middleware

    return await logging_middleware(request, call_next)


@app.get("/health")
async def health() -> JSONResponse:
    from onnxruntime import __version__ as ort_version
    from samgis_web.__version__ import __version__ as version_web
    from samgis_core.__version__ import __version__ as version_core
    from samgis_core.prediction_api.model_registry import verify_download

    variant = os.getenv("MODEL_VARIANT", "sam2.1_hiera_base_plus_uint8")
    try:
        failures = verify_download(variant, model_dir=model_folder)
        if failures:
            msg = (
                f"health_check: SHA-256 verification failed for: {', '.join(failures)}"
            )
            app_logger.error(msg)
            raise OSError(msg)
        app_logger.info(
            f"still alive, version_onnxruntime:'{ort_version}', version_web:'{version_web}', version_core:'{version_core}'."
        )
        return JSONResponse(status_code=200, content={"msg": "still alive..."})
    except OSError as e:
        app_logger.error(f"health_check error: {e}.")
        raise HTTPException(500, detail=str(e))


def infer_samgis_fn(request_input: ApiRequestBody | str) -> str:
    from samgis_web.web.web_helpers import get_parsed_bbox_points_with_dictlist_prompt

    app_logger.info("starting inference request...")
    try:
        import time

        time_start_run = time.time()
        body_request = get_parsed_bbox_points_with_dictlist_prompt(request_input)
        app_logger.info(f"body_request:{body_request}.")
        try:
            app_logger.info(f"source_name = {body_request['source_name']}.")
            output = samexporter_predict(
                bbox=body_request["bbox"],
                prompt=body_request["prompt"],
                zoom=body_request["zoom"],
                source=body_request["source"],
                source_name=body_request["source_name"],
                model_folder=model_folder,
            )
            duration_run = time.time() - time_start_run
            app_logger.info(f"duration_run:{duration_run}.")
            body = {"duration_run": duration_run, "output": output}
            dumped = json.dumps(body)
            app_logger.info(f"json.dumps(body) type:{type(dumped)}, len:{len(dumped)}.")
            app_logger.debug(f"complete json.dumps(body):{dumped}.")
            return dumped
        except Exception as inference_exception:
            app_logger.error(f"inference_exception:{inference_exception}.")
            app_logger.error(f"inference_exception, request_input:{request_input}.")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    except ValidationError as va1:
        app_logger.error(f"validation error: {str(va1)}.")
        app_logger.error(f"ValidationError, request_input:{request_input}.")
        raise RequestValidationError("Unprocessable Entity")


@app.post("/infer_samgis")
def infer_samgis(request_input: ApiRequestBody) -> JSONResponse:
    dumped = infer_samgis_fn(request_input=request_input)
    app_logger.info(f"json.dumps(body) type:{type(dumped)}, len:{len(dumped)}.")
    app_logger.debug(f"complete json.dumps(body):{dumped}.")
    return JSONResponse(status_code=200, content={"body": dumped})


@app.exception_handler(RequestValidationError)
def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    from samgis_web.web import exception_handlers

    return exception_handlers.request_validation_exception_handler(request, exc)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    from samgis_web.web import exception_handlers

    return exception_handlers.http_exception_handler(request, exc)


create_folders_if_not_exists.folders_creation(folders_map)
write_tmp_on_disk = os.getenv("WRITE_TMP_ON_DISK", "")
app_logger.info(f"write_tmp_on_disk:{write_tmp_on_disk}.")
if bool(write_tmp_on_disk):
    try:
        if not Path(write_tmp_on_disk).is_dir():
            raise OSError(
                f"error on preparing temp folder '{write_tmp_on_disk}' not found!"
            )
        app.mount(
            "/vis_output", StaticFiles(directory=write_tmp_on_disk), name="vis_output"
        )
        templates = Jinja2Templates(directory=str(project_root_folder / "static"))

        @app.get("/vis_output", response_class=HTMLResponse)
        def list_files(request: Request) -> Response:
            files = os.listdir(write_tmp_on_disk)
            files_paths = sorted([f"{request.url._url}/{f}" for f in files])
            app_logger.info(f"files_paths: '{files_paths}'")
            return templates.TemplateResponse(
                "list_files.html", {"request": request, "files": files_paths}
            )
    except (AssertionError, RuntimeError) as rerr:
        app_logger.error(
            f"{rerr} while loading the folder write_tmp_on_disk:{write_tmp_on_disk}..."
        )
        raise rerr

frontend_builder.build_frontend(
    project_root_folder=workdir,
    input_css_path=input_css_path,
    output_dist_folder=static_dist_folder,
)
app_logger.info("build_frontend ok!")

# eventually needed for tailwindcss output.css
app.mount(
    "/static", StaticFiles(directory=static_dist_folder, html=True), name="static"
)
app.mount(
    vite_index_url, StaticFiles(directory=static_dist_folder, html=True), name="index"
)


@app.get(vite_index_url)
async def index() -> FileResponse:
    return FileResponse(path=static_dist_folder / "index.html", media_type="text/html")


app_logger.info(f"Mounted index on url path {vite_index_url} .")


# add the CorrelationIdMiddleware AFTER the @app.middleware("http") decorated function to avoid missing request id
app.add_middleware(CorrelationIdMiddleware)


if __name__ == "__main__":
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=7860)
    except Exception as ex:
        app_logger.error(f"fastapi application {fastapi_title}, exception:{ex}.")
        raise ex
