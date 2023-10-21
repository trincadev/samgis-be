import json
from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.utilities.utilities import setup_logging


app = FastAPI()
local_logger = setup_logging()


class Input(BaseModel):
    name: str
    bbox: List[float]
    points_coords: List[List[float]]


@app.post("/post_test")
async def post_test(input: Input) -> JSONResponse:
    bbox = input.bbox
    name = input.name
    points_coords = input.points_coords
    return JSONResponse(
        status_code=200,
        content={
            "msg": name, "bbox": bbox, "points_coords": points_coords
        }
    )


@app.get("/hello")
async def hello() -> JSONResponse:
    return JSONResponse(status_code=200, content={"msg": "hello"})


@app.post("/infer_samgeo")
def samgeo():
    import subprocess

    from src.prediction_api.predictor import base_predict

    local_logger = setup_logging()
    local_logger.info("starting inference request...")

    try:
        import time

        time_start_run = time.time()
        # debug = True
        # local_logger = setup_logging(debug)
        message = "point_coords_segmentation"
        bbox = [-122.1497, 37.6311, -122.1203, 37.6458]
        point_coords = [[-122.1419, 37.6383]]
        try:
            output = base_predict(bbox=bbox, point_coords=point_coords)

            duration_run = time.time() - time_start_run
            body = {
                "message": message,
                "duration_run": duration_run,
                # "request_id": request_id
            }
            local_logger.info(f"body:{body}.")
            body["output"] = output
            # local_logger.info(f"End_request::{request_id}...")
            return JSONResponse(status_code=200, content={"body": json.dumps(body)})
        except Exception as inference_exception:
            home_content = subprocess.run("ls -l /home/user", shell=True, universal_newlines=True, stdout=subprocess.PIPE)
            local_logger.error(f"/home/user ls -l: {home_content.stdout}.")
            local_logger.error(f"inference error:{inference_exception}.")
            return HTTPException(status_code=500, detail="Internal server error on inference")
    except Exception as generic_exception:
        local_logger.error(f"generic error:{generic_exception}.")
        return HTTPException(status_code=500, detail="Generic internal server error")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    local_logger.error(f"exception errors: {exc.errors()}.")
    local_logger.error(f"exception body: {exc.body}.")
    headers = request.headers.items()
    local_logger.error(f'request header: {dict(headers)}.' )
    params = request.query_params.items()
    local_logger.error(f'request query params: {dict(params)}.')
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"msg": "Error - Unprocessable Entity"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    local_logger.error(f"exception: {str(exc)}.")
    headers = request.headers.items()
    local_logger.error(f'request header: {dict(headers)}.' )
    params = request.query_params.items()
    local_logger.error(f'request query params: {dict(params)}.')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"msg": "Error - Internal Server Error"}
    )


# important: the index() function and the app.mount MUST be at the end
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(path="/app/static/index.html", media_type="text/html")

