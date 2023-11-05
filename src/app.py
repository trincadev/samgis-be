import json
import time
from http import HTTPStatus
from typing import Dict
from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext

from src import app_logger
from src.prediction_api.predictors import samexporter_predict
from src.utilities.constants import CUSTOM_RESPONSE_MESSAGES


def get_response(status: int, start_time: float, request_id: str, response_body: Dict = None) -> str:
    """
    Return a response for frontend clients.

    Args:
        status: status response
        start_time: request start time (float)
        request_id: str
        response_body: dict we embed into our response

    Returns:
        str: json response

    """
    app_logger.info(f"response_body:{response_body}.")
    response_body["duration_run"] = time.time() - start_time
    response_body["message"] = CUSTOM_RESPONSE_MESSAGES[status]
    response_body["request_id"] = request_id

    response = {
        "statusCode": status,
        "header": {"Content-Type": content_types.APPLICATION_JSON},
        "body": json.dumps(response_body),
        "isBase64Encoded": False
    }
    app_logger.info(f"response type:{type(response)} => {response}.")
    return json.dumps(response)


def lambda_handler(event: dict, context: LambdaContext):
    app_logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()

    if "version" in event:
        app_logger.info(f"event version: {event['version']}.")

    try:
        app_logger.info(f"event:{json.dumps(event)}...")
        app_logger.info(f"context:{context}...")

        try:
            pt0 = 45.699, 127.1
            pt1 = 30.1, 148.492
            bbox = [pt0, pt1]
            zoom = 6
            prompt = [{"type": "rectangle", "data": [400, 460, 524, 628]}]
            body_response = {"geojson": samexporter_predict(bbox, prompt, zoom)}
            app_logger.info(f"body_response::output:{body_response}.")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except Exception as ve:
            app_logger.error(f"validation error:{ve}.")
            response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id, {})
    except Exception as e:
        app_logger.error(f"exception:{e}.")
        response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id, {})

    app_logger.info(f"response_dumped:{response}...")
    return response
