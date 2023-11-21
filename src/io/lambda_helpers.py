import json
import logging
import time
from typing import Dict
from aws_lambda_powertools.event_handler import content_types

from src import app_logger
from src.io.coordinates_pixel_conversion import get_latlng_to_pixel_coordinates
from src.utilities.constants import CUSTOM_RESPONSE_MESSAGES
from src.utilities.type_hints import RawRequestInput
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
    app_logger.debug(f"response type:{type(response)} => {response}.")
    return json.dumps(response)


def get_parsed_bbox_points(request_input: RawRequestInput) -> Dict:
    app_logger.info(f"try to parsing input request {request_input}...")

    bbox = request_input.bbox
    app_logger.debug(f"request bbox: {type(bbox)}, value:{bbox}.")
    ne = bbox.ne
    sw = bbox.sw
    app_logger.debug(f"request ne: {type(ne)}, value:{ne}.")
    app_logger.debug(f"request sw: {type(sw)}, value:{sw}.")
    ne_latlng = [float(ne.lat), float(ne.lng)]
    sw_latlng = [float(sw.lat), float(sw.lng)]
    new_zoom = int(request_input.zoom)
    new_prompt_list = []
    for prompt in request_input.prompt:
        app_logger.debug(f"current prompt: {type(prompt)}, value:{prompt}.")
        current_point = get_latlng_to_pixel_coordinates(ne, sw, prompt.data, new_zoom, prompt.type)
        app_logger.debug(f"current prompt: {type(current_point)}, value:{current_point}.")
        new_prompt_data = [current_point['x'], current_point['y']]
        app_logger.debug(f"new_prompt_data: {type(new_prompt_data)}, value:{new_prompt_data}.")
        new_prompt = {
            "type": prompt.type,
            "data": new_prompt_data
        }
        if prompt.label is not None:
            new_prompt["label"] = prompt.label
        new_prompt_list.append(new_prompt)

    app_logger.debug(f"bbox => {bbox}.")
    app_logger.debug(f'request_input-prompt updated => {new_prompt_list}.')

    app_logger.info(f"unpacking elaborated request...")
    return {
        "bbox": [ne_latlng, sw_latlng],
        "prompt": new_prompt_list,
        "zoom": new_zoom
    }


def get_parsed_request_body(event):
    app_logger.info(f"event:{json.dumps(event)}...")
    try:
        raw_body = event["body"]
    except Exception as e_constants1:
        app_logger.error(f"e_constants1:{e_constants1}.")
        raw_body = event
    app_logger.debug(f"raw_body, #1: {type(raw_body)}, {raw_body}...")
    if isinstance(raw_body, str):
        body_decoded_str = base64_decode(raw_body)
        app_logger.debug(f"body_decoded_str: {type(body_decoded_str)}, {body_decoded_str}...")
        raw_body = json.loads(body_decoded_str)
    app_logger.info(f"body, #2: {type(raw_body)}, {raw_body}...")

    parsed_body = RawRequestInput.model_validate(raw_body)
    log_level = "DEBUG" if parsed_body.debug else "INFO"
    app_logger.setLevel(log_level)
    app_logger.warning(f"set log level to {logging.getLevelName(app_logger.log_level)}.")

    return parsed_body
