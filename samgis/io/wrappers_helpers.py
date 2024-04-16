"""lambda helper functions"""
import logging
from sys import stdout
from typing import Dict

import loguru
from xyzservices import providers, TileProvider

from samgis import app_logger
from samgis.io.coordinates_pixel_conversion import get_latlng_to_pixel_coordinates
from samgis.utilities.constants import COMPLETE_URL_TILES_MAPBOX, COMPLETE_URL_TILES_NEXTZEN, CUSTOM_RESPONSE_MESSAGES
from samgis.utilities.type_hints import ApiRequestBody, ContentTypes, XYZTerrainProvidersNames, XYZDefaultProvidersNames
from samgis_core.utilities.utilities import base64_decode


def get_response(status: int, start_time: float, request_id: str, response_body: Dict = None) -> str:
    """
    Response composer

    Args:
        status: status response
        start_time: request start time (float)
        request_id: str
        response_body: dict we embed into our response

    Returns:
        json response

    """
    from json import dumps
    from time import time

    app_logger.debug(f"response_body:{response_body}.")
    response_body["duration_run"] = time() - start_time
    response_body["message"] = CUSTOM_RESPONSE_MESSAGES[status]
    response_body["request_id"] = request_id

    response = {
        "statusCode": status,
        "header": {"Content-Type": ContentTypes.APPLICATION_JSON},
        "body": dumps(response_body),
        "isBase64Encoded": False
    }
    app_logger.debug(f"response type:{type(response)} => {response}.")
    return dumps(response)


def get_parsed_bbox_points(request_input: ApiRequestBody) -> Dict:
    """
    Parse the raw input request into bbox, prompt and zoom

    Args:
        request_input: input dict

    Returns:
        dict with bounding box, prompt and zoom
    """

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
    new_prompt_list = _get_parsed_prompt_list(ne, sw, new_zoom, request_input.prompt)

    app_logger.debug(f"bbox => {bbox}.")
    app_logger.debug(f'request_input-prompt updated => {new_prompt_list}.')

    app_logger.info("unpacking elaborated request...")
    return {
        "bbox": [ne_latlng, sw_latlng],
        "prompt": new_prompt_list,
        "zoom": new_zoom,
        "source": get_url_tile(request_input.source_type)
    }


def _get_parsed_prompt_list(bbox_ne, bbox_sw, zoom, prompt_list):
    new_prompt_list = []
    for prompt in prompt_list:
        app_logger.debug(f"current prompt: {type(prompt)}, value:{prompt}.")
        new_prompt = {"type": prompt.type.value}
        if prompt.type == "point":
            new_prompt_data = _get_new_prompt_data_point(bbox_ne, bbox_sw, prompt, zoom)
            new_prompt["label"] = prompt.label.value
        elif prompt.type == "rectangle":
            new_prompt_data = _get_new_prompt_data_rectangle(bbox_ne, bbox_sw, prompt, zoom)
        else:
            msg = "Valid prompt type: 'point' or 'rectangle', not '{}'. Check ApiRequestBody parsing/validation."
            raise TypeError(msg.format(prompt.type))
        app_logger.debug(f"new_prompt_data: {type(new_prompt_data)}, value:{new_prompt_data}.")
        new_prompt["data"] = new_prompt_data
        new_prompt_list.append(new_prompt)
    return new_prompt_list


def _get_new_prompt_data_point(bbox_ne, bbox_sw, prompt, zoom):
    current_point = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data, zoom, prompt.type)
    app_logger.debug(f"current prompt: {type(current_point)}, value:{current_point}, label: {prompt.label}.")
    return [current_point['x'], current_point['y']]


def _get_new_prompt_data_rectangle(bbox_ne, bbox_sw, prompt, zoom):
    current_point_ne = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data.ne, zoom, prompt.type)
    app_logger.debug(
        f"rectangle:: current_point_ne prompt: {type(current_point_ne)}, value:{current_point_ne}.")
    current_point_sw = get_latlng_to_pixel_coordinates(bbox_ne, bbox_sw, prompt.data.sw, zoom, prompt.type)
    app_logger.debug(
        f"rectangle:: current_point_sw prompt: {type(current_point_sw)}, value:{current_point_sw}.")
    # correct order for rectangle prompt
    return [
        current_point_sw["x"],
        current_point_ne["y"],
        current_point_ne["x"],
        current_point_sw["y"]
    ]


def get_parsed_request_body(event: Dict or str) -> ApiRequestBody:
    """
    Validator for the raw input request lambda event

    Args:
        event: input dict

    Returns:
        parsed request input
    """
    from json import dumps, loads
    from logging import getLevelName

    def _get_current_log_level(logger: loguru.logger) -> [str, loguru._logger.Level]:
        levels = logger._core.levels
        current_log_level = logger._core.min_level
        level_filt = [l for l in levels.items() if l[1].no == current_log_level]
        return level_filt[0]

    app_logger.info(f"event:{dumps(event)}...")
    try:
        raw_body = event["body"]
    except Exception as e_constants1:
        app_logger.error(f"e_constants1:{e_constants1}.")
        raw_body = event
    app_logger.debug(f"raw_body, #1: {type(raw_body)}, {raw_body}...")
    if isinstance(raw_body, str):
        body_decoded_str = base64_decode(raw_body)
        app_logger.debug(f"body_decoded_str: {type(body_decoded_str)}, {body_decoded_str}...")
        raw_body = loads(body_decoded_str)
    app_logger.info(f"body, #2: {type(raw_body)}, {raw_body}...")

    parsed_body = ApiRequestBody.model_validate(raw_body)
    log_level = "DEBUG" if parsed_body.debug else "INFO"
    app_logger.remove()
    app_logger.add(stdout, level=log_level)
    try:
        current_log_level_name, _ = _get_current_log_level(app_logger)
        app_logger.warning(f"set log level to {getLevelName(current_log_level_name)}.")
    except Exception as ex:
        print("failing setting parsing bbox, logger is ok? ex:", ex, "#")

    return parsed_body


mapbox_terrain_rgb = TileProvider(
    name=XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME,
    url=COMPLETE_URL_TILES_MAPBOX,
    attribution=""
)
nextzen_terrain_rgb = TileProvider(
    name=XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME,
    url=COMPLETE_URL_TILES_NEXTZEN,
    attribution=""
)


def get_url_tile(source_type: str):
    try:
        match source_type.lower():
            case XYZDefaultProvidersNames.DEFAULT_TILES_NAME_SHORT:
                return providers.query_name(XYZDefaultProvidersNames.DEFAULT_TILES_NAME)
            case XYZTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME:
                return mapbox_terrain_rgb
            case XYZTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME:
                app_logger.info("nextzen_terrain_rgb:", nextzen_terrain_rgb)
                return nextzen_terrain_rgb
            case _:
                return providers.query_name(source_type)
    except ValueError as ve:
        from pydantic_core import ValidationError

        app_logger.error("ve:", str(ve))
        raise ValidationError(ve)


def check_source_type_is_terrain(source: str | TileProvider):
    return isinstance(source, TileProvider) and source.name in list(XYZTerrainProvidersNames)


def get_source_name(source: str | TileProvider) -> str | bool:
    try:
        match source.lower():
            case XYZDefaultProvidersNames.DEFAULT_TILES_NAME_SHORT:
                source_output = providers.query_name(XYZDefaultProvidersNames.DEFAULT_TILES_NAME)
            case _:
                source_output = providers.query_name(source)
        if isinstance(source_output, str):
            return source_output
        try:
            source_dict = dict(source_output)
            app_logger.info(f"source_dict:{type(source_dict)}, {'name' in source_dict}, source_dict:{source_dict}.")
            return source_dict["name"]
        except KeyError as ke:
            app_logger.error(f"ke:{ke}.")
    except ValueError as ve:
        app_logger.info(f"source name::{source}, ve:{ve}.")
    app_logger.info(f"source name::{source}.")

    return False
