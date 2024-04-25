import json
import os
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from samgis import PROJECT_ROOT_FOLDER
from samgis.io.wrappers_helpers import get_parsed_bbox_points, get_source_name
from samgis.utilities.type_hints import ApiRequestBody
from samgis_core.utilities.fastapi_logger import setup_logging
from samgis.prediction_api.predictors import samexporter_predict


app_logger = setup_logging(debug=True)
app_logger.info(f"PROJECT_ROOT_FOLDER:{PROJECT_ROOT_FOLDER}.")
app = FastAPI()


@app.middleware("http")
async def request_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    with app_logger.contextualize(request_id=request_id):
        app_logger.info("Request started")

        try:
            response = await call_next(request)

        except Exception as ex:
            app_logger.error(f"Request failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)

        finally:
            response.headers["X-Request-ID"] = request_id
            app_logger.info("Request ended")

        return response


@app.post("/post_test")
async def post_test(request_input: ApiRequestBody) -> JSONResponse:
    request_body = get_parsed_bbox_points(request_input)
    app_logger.info(f"request_body:{request_body}.")
    return JSONResponse(
        status_code=200,
        content=get_parsed_bbox_points(request_input)
    )


@app.get("/health")
async def health() -> JSONResponse:
    from samgis.__version__ import __version__ as version
    from samgis_core.__version__ import __version__ as version_core

    app_logger.info(f"still alive, version:{version}, version_core:{version_core}.")
    return JSONResponse(status_code=200, content={"msg": "still alive..."})


@app.post("/infer_samgis")
def infer_samgis(request_input: ApiRequestBody) -> JSONResponse:
    app_logger.info("starting inference request...")

    try:
        import time

        time_start_run = time.time()
        body_request = get_parsed_bbox_points(request_input)
        app_logger.info(f"body_request:{body_request}.")
        try:
            source_name = get_source_name(request_input.source_type)
            app_logger.info(f"source_name = {source_name}.")
            output = samexporter_predict(
                bbox=body_request["bbox"], prompt=body_request["prompt"], zoom=body_request["zoom"],
                source=body_request["source"], source_name=source_name
            )
            duration_run = time.time() - time_start_run
            app_logger.info(f"duration_run:{duration_run}.")
            body = {
                "duration_run": duration_run,
                "output": output
            }
            return JSONResponse(status_code=200, content={"body": json.dumps(body)})
        except Exception as inference_exception:
            import subprocess
            home_content = subprocess.run(
                "ls -l /var/task", shell=True, universal_newlines=True, stdout=subprocess.PIPE
            )
            app_logger.error(f"/home/user ls -l: {home_content.stdout}.")
            app_logger.error(f"inference error:{inference_exception}.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error on inference")
    except ValidationError as va1:
        app_logger.error(f"validation error: {str(va1)}.")
        raise ValidationError("Unprocessable Entity")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    app_logger.error(f"exception errors: {exc.errors()}.")
    app_logger.error(f"exception body: {exc.body}.")
    headers = request.headers.items()
    app_logger.error(f'request header: {dict(headers)}.')
    params = request.query_params.items()
    app_logger.error(f'request query params: {dict(params)}.')
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"msg": "Error - Unprocessable Entity"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    app_logger.error(f"exception: {str(exc)}.")
    headers = request.headers.items()
    app_logger.error(f'request header: {dict(headers)}.')
    params = request.query_params.items()
    app_logger.error(f'request query params: {dict(params)}.')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"msg": "Error - Internal Server Error"}
    )


write_tmp_on_disk = os.getenv("WRITE_TMP_ON_DISK", "")
app_logger.info(f"write_tmp_on_disk:{write_tmp_on_disk}.")
if bool(write_tmp_on_disk):
    app.mount("/vis_output", StaticFiles(directory=write_tmp_on_disk), name="vis_output")
    templates = Jinja2Templates(directory=PROJECT_ROOT_FOLDER / "static")


    @app.get("/vis_output", response_class=HTMLResponse)
    def list_files(request: Request):

        files = os.listdir(write_tmp_on_disk)
        files_paths = sorted([f"{request.url._url}/{f}" for f in files])
        print(files_paths)
        return templates.TemplateResponse(
            "list_files.html", {"request": request, "files": files_paths}
        )


# important: the index() function and the app.mount MUST be at the end
app.mount("/", StaticFiles(directory=PROJECT_ROOT_FOLDER / "static" / "dist", html=True), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(path="/app/static/index.html", media_type="text/html")

