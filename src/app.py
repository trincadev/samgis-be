import json
import time
from http import HTTPStatus
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import content_types, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, ValidationError

from src.utilities.type_hints import input_floatlist, input_floatlist2


logger = Logger()


class JSONResponse(Response):
    def response_to_json(self):
        return json.dumps(self.__dict__)


class BBoxWithPointInput(BaseModel):
    bbox: input_floatlist
    points: input_floatlist2
    duration_run: float = 0
    message: str = ""
    request_id: str = ""


def get_response(status: int, start_time: float, request_id: str, output: BBoxWithPointInput = None) -> str:
    """
    Return a response for frontend clients.

    Args:
        status: status response
        start_time: request start time (float)
        request_id: str
        output: dict we embed into our response

    Returns:
        dict: response

    """
    messages = {200: "ok", 422: "validation error", 500: "internal server error"}
    body = f"{messages[status]}, request_id: {request_id}."
    if status == 200:
        output.duration_run = time.time() - start_time
        output.message = messages[status]
        output.request_id = request_id
        body = output.model_dump_json()
    response = JSONResponse(
        status_code=status,
        content_type=content_types.APPLICATION_JSON if status == 200 else content_types.TEXT_PLAIN,
        body=body
    )
    logger.info(f"response type:{type(response)} => {response}.")
    return response.response_to_json()


def lambda_handler(event: dict, context: LambdaContext):
    logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()
    try:
        logger.debug(f"event:{json.dumps(event)}...")
        logger.debug(f"context:{context}...")

        try:
            bbox_points = BBoxWithPointInput(bbox=event["bbox"], points=event["points"])
            logger.info(f"validation ok, bbox_points:{bbox_points}...")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, bbox_points)
        except ValidationError as ve:
            logger.error(f"validation error:{ve}.")
            response = get_response(422, start_time, context.aws_request_id)
    except Exception as e:
        logger.error(f"exception:{e}.")
        response = get_response(500, start_time, context.aws_request_id)

    logger.info(f"response_dumped:{response}...")
    return response
