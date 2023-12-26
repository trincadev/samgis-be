"""Lambda entry point"""
from http import HTTPStatus
from typing import Dict

from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from samgis import app_logger
from samgis.io.lambda_helpers import get_parsed_request_body, get_parsed_bbox_points, get_response
from samgis.prediction_api.predictors import samexporter_predict


def lambda_handler(event: Dict, context: LambdaContext) -> str:
    """
    Handle the request for the serverless backend and return the response
    (success or a type of error based on the exception raised).

    Args:
        event: request content
        context: request context

    Returns:
        json response from get_response() function

    """
    from time import time
    app_logger.info(f"start with aws_request_id:{context.aws_request_id}.")
    start_time = time()

    if "version" in event:
        app_logger.info(f"event version: {event['version']}.")

    try:
        app_logger.info("try get_parsed_event...")
        request_input = get_parsed_request_body(event)
        app_logger.info("event parsed: ok")
        body_request = get_parsed_bbox_points(request_input)
        app_logger.info(f"body_request => {type(body_request)}, {body_request}.")

        try:
            body_response = samexporter_predict(
                body_request["bbox"], body_request["prompt"], body_request["zoom"], source=body_request["source"]
            )
            app_logger.info(f"output body_response length:{len(body_response)}.")
            app_logger.debug(f"output body_response:{body_response}.")
            response = get_response(HTTPStatus.OK.value, start_time, context.aws_request_id, body_response)
        except Exception as ex2:
            app_logger.exception(f"exception2:{ex2}.", exc_info=True)
            response = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, context.aws_request_id, {})
    except ValidationError as va1:
        app_logger.exception(f"ValidationError:{va1}.", exc_info=True)
        response = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, context.aws_request_id, {})
    except Exception as ex1:
        app_logger.exception(f"exception1:{ex1}.", exc_info=True)
        response = get_response(HTTPStatus.BAD_REQUEST.value, start_time, context.aws_request_id, {})

    app_logger.debug(f"response_dumped:{response}...")
    return response
