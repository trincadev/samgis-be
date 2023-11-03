import json
import time
from http import HTTPStatus
from typing import Dict, List

from aws_lambda_powertools.event_handler import content_types
from aws_lambda_powertools.utilities.typing import LambdaContext
from geojson_pydantic import FeatureCollection, Feature, Polygon
from pydantic import BaseModel, ValidationError

from src import app_logger
from src.prediction_api.predictor import base_predict
from src.utilities.constants import CUSTOM_RESPONSE_MESSAGES, MODEL_NAME, ZOOM
from src.utilities.utilities import base64_decode

PolygonFeatureCollectionModel = FeatureCollection[Feature[Polygon, Dict]]


class LatLngTupleLeaflet(BaseModel):
    lat: float
    lng: float


class RequestBody(BaseModel):
    ne: LatLngTupleLeaflet
    sw: LatLngTupleLeaflet
    points: List[LatLngTupleLeaflet]
    model: str = MODEL_NAME
    zoom: float = ZOOM


class ResponseBody(BaseModel):
    geojson: Dict = None
    request_id: str
    duration_run: float
    message: str


def get_response(status: int, start_time: float, request_id: str, response_body: ResponseBody = None) -> str:
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
    response_body.duration_run = time.time() - start_time
    response_body.message = CUSTOM_RESPONSE_MESSAGES[status]
    response_body.request_id = request_id

    response = {
        "statusCode": status,
        "header": {"Content-Type": content_types.APPLICATION_JSON},
        "body": response_body.model_dump_json(),
        "isBase64Encoded": False
    }
    app_logger.info(f"response type:{type(response)} => {response}.")
    return json.dumps(response)


def get_parsed_bbox_points(request_input: RequestBody) -> Dict:
    return {
        "bbox": [
            request_input.ne.lat, request_input.sw.lat,
            request_input.ne.lng, request_input.sw.lng
        ],
        "points": [[p.lat, p.lng] for p in request_input.points]
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
            model_name = body["model"] if "model" in body else MODEL_NAME
            zoom = body["zoom"] if "zoom" in body else ZOOM
            body_request_validated = RequestBody(ne=body["ne"], sw=body["sw"], points=body["points"], model=model_name, zoom=zoom)
            body_request = get_parsed_bbox_points(body_request_validated)
            app_logger.info(f"validation ok - body_request:{body_request}, starting prediction...")
            output_geojson_dict = base_predict(bbox=body_request["bbox"], model_name=body_request_validated["model"], zoom=body_request_validated["zoom"])

            # raise ValidationError in case this is not a valid geojson by GeoJSON specification rfc7946
            PolygonFeatureCollectionModel(**output_geojson_dict)
            body_response = ResponseBody(geojson=output_geojson_dict)
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except ValidationError as ve:
            app_logger.error(f"validation error:{ve}.")
            response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id)
    except Exception as e:
        app_logger.error(f"exception:{e}.")
        response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id)

    app_logger.info(f"response_dumped:{response}...")
    return response
