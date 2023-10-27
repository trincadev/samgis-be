import json
import time
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, ValidationError

from src.utilities.type_hints import input_floatlist, input_floatlist2


logger = Logger()


class BBoxWithPointInput(BaseModel):
    bbox: input_floatlist
    points: input_floatlist2


def get_response(status: int, start_time: float, output: BaseModel = None) -> dict[str]:
    """
    Return a response for frontend clients.

    Args:
        status: status response
        start_time: request start time (float)
        output: dict we embed into our response

    Returns:
        dict: response

    """
    messages = {200: "ok", 422: "validation error", 500: "internal server error"}
    body = {"duration_run": time.time() - start_time, "message": messages[status]}
    if status == 200:
        body = {"output": output.model_dump_json(), **body}
    return {
        "statusCode": status,
        "headers": {'Content-type': 'application/json', 'Accept': 'application/json'},
        "body": json.dumps(body)
    }


def lambda_handler(event: dict, context: LambdaContext) -> dict[str]:
    logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()
    try:
        logger.debug(f"event:{json.dumps(event)}...")
        logger.debug(f"context:{context}...")

        try:
            bbox_points = BBoxWithPointInput(bbox=event["bbox"], points=event["points"])
            logger.info(f"validation ok, bbox_points:{bbox_points}...")
            response = get_response(200, start_time, bbox_points)
        except ValidationError as ve:
            logger.error(f"validation error:{ve}.")
            response = get_response(422, start_time)
    except Exception as e:
        logger.error(f"exception:{e}.")
        response = get_response(500, start_time)

    logger.info(f"response:{response}...")
    return response
