import json
import uuid

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from samgis import app_logger
from samgis.io.lambda_helpers import get_parsed_bbox_points
from samgis.utilities.type_hints import ApiRequestBody

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
            app_logger.info(f"Request ended")
            return response


@app.post("/post_test")
async def post_test(request_input: ApiRequestBody) -> JSONResponse:
    request_body = get_parsed_bbox_points(request_input)
    app_logger.info(f"request_body:{request_body}.")
    return JSONResponse(
        status_code=200,
        content=get_parsed_bbox_points(request_input)
    )


@app.get("/hello")
async def hello() -> JSONResponse:
    app_logger.info(f"hello")
    return JSONResponse(status_code=200, content={"msg": "hello"})


@app.post("/infer_samgis")
def samgis(request_input: ApiRequestBody):
    import subprocess

    from samgis.prediction_api.predictors import samexporter_predict
    app_logger.info("starting inference request...")

    try:
        import time

        time_start_run = time.time()
        body_request = get_parsed_bbox_points(request_input)
        app_logger.info(f"body_request:{body_request}.")
        try:
            output = samexporter_predict(
                bbox=body_request["bbox"], prompt=body_request["prompt"], zoom=body_request["zoom"],
                source=body_request["source"]
            )
            duration_run = time.time() - time_start_run
            app_logger.info(f"duration_run:{duration_run}.")
            body = {
                "duration_run": duration_run,
                "output": output
            }
            return JSONResponse(status_code=200, content={"body": json.dumps(body)})
        except Exception as inference_exception:
            home_content = subprocess.run(
                "ls -l /var/task", shell=True, universal_newlines=True, stdout=subprocess.PIPE
            )
            app_logger.error(f"/home/user ls -l: {home_content.stdout}.")
            app_logger.error(f"inference error:{inference_exception}.")
            return HTTPException(status_code=500, detail="Internal server error on inference")
    except Exception as generic_exception:
        app_logger.error(f"generic error:{generic_exception}.")
        return HTTPException(status_code=500, detail="Generic internal server error")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    app_logger.error(f"exception errors: {exc.errors()}.")
    app_logger.error(f"exception body: {exc.body}.")
    headers = request.headers.items()
    app_logger.error(f'request header: {dict(headers)}.' )
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
    app_logger.error(f'request header: {dict(headers)}.' )
    params = request.query_params.items()
    app_logger.error(f'request query params: {dict(params)}.')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"msg": "Error - Internal Server Error"}
    )


# important: the index() function and the app.mount MUST be at the end
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(path="/app/static/index.html", media_type="text/html")

