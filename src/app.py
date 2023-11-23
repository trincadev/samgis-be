"""Lambda entry point"""
import time
from http import HTTPStatus

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from src import app_logger
from src.io.lambda_helpers import get_parsed_request_body, get_parsed_bbox_points, get_response
from src.prediction_api.predictors import samexporter_predict


def lambda_handler(event: dict, context: LambdaContext):
    """
    Handle the request for the serverless backend, dispatch the response.

    Args:
        event: request content
        context: request context

    Returns:
        dict: response from try_return_output() function

    """
    app_logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time.time()

    if "version" in event:
        app_logger.info(f"event version: {event['version']}.")

    try:
        app_logger.info(f"try get_parsed_event...")
        request_input = get_parsed_request_body(event)
        app_logger.info(f"event parsed: ok")
        body_request = get_parsed_bbox_points(request_input)

        try:
            app_logger.info(f"body_request => {type(body_request)}, {body_request}.")
            body_response = samexporter_predict(body_request["bbox"], body_request["prompt"], body_request["zoom"])
            app_logger.info(f"output body_response:{body_response}.")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except Exception as ex2:
            app_logger.error(f"exception2:{ex2}.")
            response = get_response(HTTPStatus.BAD_REQUEST.value, start_time, context.aws_request_id, {})
    except ValidationError as va1:
        app_logger.error(f"ValidationError:{va1}.")
        response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id, {})
    except Exception as ex1:
        app_logger.error(f"exception1:{ex1}.")
        response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id, {})

    app_logger.info(f"response_dumped:{response}...")
    return response
