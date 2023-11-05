import json
import time
from http import HTTPStatus
from typing import Dict

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext

from src import app_logger
from src.prediction_api.predictors import samexporter_predict
from src.utilities.constants import CUSTOM_RESPONSE_MESSAGES
from src.utilities.utilities import base64_decode


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


def get_parsed_bbox_points(request_input: Dict) -> Dict:
    app_logger.info(f"try to parsing input request {request_input}...")
    ne = request_input["ne"]
    sw = request_input["sw"]
    bbox = [
        [float(ne["lat"]), float(ne["lng"])],
        [float(sw["lat"]), float(sw["lng"])]
    ]
    app_logger.info(f"bbox {bbox}.")

    app_logger.info(f"unpacking {request_input}...")
    return {
        "bbox": bbox,
        "prompt": request_input["prompt"],
        "zoom": int(request_input["zoom"])
    }


def lambda_handler(event: dict, context: LambdaContext):
    app_logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()

    if "version" in event:
        app_logger.info(f"event version: {event['version']}.")

    try:
        app_logger.info(f"event:{json.dumps(event)}...")
        app_logger.info(f"context:{context}...")

        try:
            body = event["body"]
        except Exception as e_constants1:
            app_logger.error(f"e_constants1:{e_constants1}.")
            body = event

        app_logger.info(f"body: {type(body)}, {body}...")

        if isinstance(body, str):
            body_decoded_str = base64_decode(body)
            app_logger.info(f"body_decoded_str: {type(body_decoded_str)}, {body_decoded_str}...")
            body = json.loads(body_decoded_str)

        app_logger.info(f"body:{body}...")

        try:
            body_request = get_parsed_bbox_points(body)
            body_response = samexporter_predict(body_request["bbox"], body_request["prompt"], body_request["zoom"])
            app_logger.info(f"body_response::output:{body_response}.")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except Exception as ex2:
            app_logger.error(f"exception2:{ex2}.")
            response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id, {})
    except Exception as ex1:
        app_logger.error(f"exception1:{ex1}.")
        response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id, {})

    app_logger.info(f"response_dumped:{response}...")
    return response
