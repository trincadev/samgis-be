import json
import time
from http import HTTPStatus
from typing import Dict, List

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import BaseModel

from src import app_logger
from src.io.coordinates_pixel_conversion import get_latlng_to_pixel_coordinates
from src.prediction_api.predictors import samexporter_predict
from src.utilities.constants import CUSTOM_RESPONSE_MESSAGES, DEFAULT_LOG_LEVEL
from src.utilities.utilities import base64_decode


list_float = List[float]
llist_float = List[list_float]


class LatLngDict(BaseModel):
    lat: float
    lng: float


class RawBBox(BaseModel):
    ne: LatLngDict
    sw: LatLngDict


class RawPrompt(BaseModel):
    type: str
    data: LatLngDict
    label: int = 0


class RawRequestInput(BaseModel):
    bbox: RawBBox
    prompt: RawPrompt
    zoom: int | float
    source_type: str = "Satellite"


class ParsedPrompt(BaseModel):
    type: str
    data: llist_float
    label: int = 0


class ParsedRequestInput(BaseModel):
    bbox: llist_float
    prompt: ParsedPrompt
    zoom: int | float


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
    app_logger.debug(f"response type:{type(response)} => {response}.")
    return json.dumps(response)


def get_parsed_bbox_points(request_input: RawRequestInput) -> Dict:
    app_logger.info(f"try to parsing input request {request_input}...")
    bbox = request_input["bbox"]
    app_logger.debug(f"request bbox: {type(bbox)}, value:{bbox}.")
    ne = bbox["ne"]
    sw = bbox["sw"]
    app_logger.debug(f"request ne: {type(ne)}, value:{ne}.")
    app_logger.debug(f"request sw: {type(sw)}, value:{sw}.")
    ne_latlng = [float(ne["lat"]), float(ne["lng"])]
    sw_latlng = [float(sw["lat"]), float(sw["lng"])]
    bbox = [ne_latlng, sw_latlng]
    zoom = int(request_input["zoom"])
    for prompt in request_input["prompt"]:
        app_logger.debug(f"current prompt: {type(prompt)}, value:{prompt}.")
        data = prompt["data"]
        if prompt["type"] == "point":
            current_point = get_latlng_to_pixel_coordinates(ne, sw, data, zoom, "point")
            app_logger.debug(f"current prompt: {type(current_point)}, value:{current_point}.")
            new_prompt_data = [current_point['x'], current_point['y']]
            app_logger.debug(f"new_prompt_data: {type(new_prompt_data)}, value:{new_prompt_data}.")
            prompt["data"] = new_prompt_data
        else:
            raise ValueError("valid prompt type is only 'point'")

    app_logger.debug(f"bbox => {bbox}.")
    app_logger.debug(f'request_input-prompt updated => {request_input["prompt"]}.')

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
        body = get_parsed_request_body(context, event)

        try:
            prompt_latlng = body["prompt"]
            app_logger.debug(f"prompt_latlng:{prompt_latlng}.")
            body_request = get_parsed_bbox_points(body)
            app_logger.info(f"body_request=> {type(body_request)}, {body_request}.")
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


def get_parsed_request_body(context, event):
    app_logger.info(f"event:{json.dumps(event)}...")
    app_logger.info(f"context:{context}...")
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
        log_level = 'DEBUG' if body['debug'] else DEFAULT_LOG_LEVEL
        app_logger.warning(f"set logger level to DEBUG")
        app_logger.setLevel(log_level)
    except KeyError:
        app_logger.warning(f"can't set log level, reset it...")
        app_logger.setLevel(DEFAULT_LOG_LEVEL)
    app_logger.warning(f"logger level is {app_logger.log_level}.")
    return body
