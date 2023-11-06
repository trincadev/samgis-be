import json
import time
from http import HTTPStatus
from typing import Dict

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext

from src import app_logger
from src.io.coordinates_pixel_conversion import get_point_latlng_to_pixel_coordinates, get_latlng_to_pixel_coordinates
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
    app_logger.debug(f"response_body:{response_body}.")
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
    ne_latlng = [float(ne["lat"]), float(ne["lng"])]
    sw_latlng = [float(sw["lat"]), float(sw["lng"])]
    bbox = [ne_latlng, sw_latlng]
    zoom = int(request_input["zoom"])
    for prompt in request_input["prompt"]:
        app_logger.info(f"current prompt: {type(prompt)}, value:{prompt}.")
        data = prompt["data"]
        app_logger.info(f"current data point: {type(data)}, value:{data}.")

        diff_pixel_coordinates_ne = get_latlng_to_pixel_coordinates(ne, data, zoom)
        app_logger.info(f'current data by current prompt["data"]: {type(data)}, {data} => {diff_pixel_coordinates_ne}.')
        prompt["data"] = [diff_pixel_coordinates_ne["x"], diff_pixel_coordinates_ne["y"]]

    app_logger.debug(f"bbox {bbox}.")
    app_logger.debug(f'request_input["prompt"]:{request_input["prompt"]}.')

    app_logger.info(f"unpacking elaborated {request_input}...")
    return {
        "bbox": bbox,
        "prompt": request_input["prompt"],
        "zoom": zoom
    }


def lambda_handler(event: dict, context: LambdaContext):
    app_logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()

    if "version" in event:
        app_logger.info(f"event version: {event['version']}.")

    try:
        app_logger.debug(f"event:{json.dumps(event)}...")
        app_logger.debug(f"context:{context}...")

        try:
            body = event["body"]
        except Exception as e_constants1:
            app_logger.error(f"e_constants1:{e_constants1}.")
            body = event

        app_logger.debug(f"body, #1: {type(body)}, {body}...")

        if isinstance(body, str):
            body_decoded_str = base64_decode(body)
            app_logger.debug(f"body_decoded_str: {type(body_decoded_str)}, {body_decoded_str}...")
            body = json.loads(body_decoded_str)

        app_logger.info(f"body, #2: {type(body)}, {body}...")

        try:
            body_request = get_parsed_bbox_points(body)
            body_response = samexporter_predict(body_request["bbox"], body_request["prompt"], body_request["zoom"])
            app_logger.info(f"output body_response:{body_response}.")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except Exception as ex2:
            app_logger.error(f"exception2:{ex2}.")
            response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id, {})
    except Exception as ex1:
        app_logger.error(f"exception1:{ex1}.")
        response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id, {})

    app_logger.info(f"response_dumped:{response}...")
    return response
