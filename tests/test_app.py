import json
import time
import unittest
from unittest.mock import patch

from awslambdaric.lambda_context import LambdaContext

from src import app


class TestAppFailures(unittest.TestCase):
    @patch.object(time, "time")
    @patch.object(app, "samexporter_predict")
    @patch.object(app, "get_parsed_bbox_points")
    @patch.object(app, "get_parsed_request_body")
    def test_lambda_handler_400(
            self,
            get_parsed_request_body_mocked,
            get_parsed_bbox_points_mocked,
            samexporter_predict_mocked,
            time_mocked
    ):
        from src.app import lambda_handler

        time_mocked.return_value = 0
        get_parsed_request_body_mocked.value = {}
        get_parsed_bbox_points_mocked.return_value = {"bbox": "bbox_object", "prompt": "prompt_object", "zoom": 1}
        samexporter_predict_mocked.side_effect = ValueError("I raise a value error!")

        event = {"body": {}, "version": 1.0}
        lambda_context = LambdaContext(
            invoke_id="test_invoke_id",
            client_context=None,
            cognito_identity=None,
            epoch_deadline_time_in_ms=time.time()
        )
        expected_response_400 = '{"statusCode": 400, "header": {"Content-Type": "application/json"}, '
        expected_response_400 += '"body": "{\\"duration_run\\": 0, \\"message\\": \\"Bad Request\\", '
        expected_response_400 += '\\"request_id\\": \\"test_invoke_id\\"}", "isBase64Encoded": false}'

        response_400 = lambda_handler(event, lambda_context)
        assert response_400 == expected_response_400

    @patch.object(time, "time")
    @patch.object(app, "get_parsed_request_body")
    def test_lambda_handler_500(self, get_parsed_request_body_mocked, time_mocked):
        from src.app import lambda_handler

        time_mocked.return_value = 0
        get_parsed_request_body_mocked.return_value = {}

        event = {"body": {}, "version": 1.0}
        lambda_context = LambdaContext(
            invoke_id="test_invoke_id",
            client_context=None,
            cognito_identity=None,
            epoch_deadline_time_in_ms=time.time()
        )

        response_500 = lambda_handler(event, lambda_context)
        check_500 = response_500 == (
            '{"statusCode": 500, "header": {"Content-Type": "application/json"}, '
            '"body": "{\\"duration_run\\": 0, \\"message\\": \\"Internal server error\\", '
            '\\"request_id\\": \\"test_invoke_id\\"}", "isBase64Encoded": false}')
        print(f"test_lambda_handler_422:{check_500}.")
        assert check_500
        print("check_500")

    @patch.object(time, "time")
    def test_lambda_handler_422(self, time_mocked):
        from src.app import lambda_handler

        time_mocked.return_value = 0
        event = {"body": {}, "version": 1.0}
        lambda_context = LambdaContext(
            invoke_id="test_invoke_id",
            client_context=None,
            cognito_identity=None,
            epoch_deadline_time_in_ms=time.time()
        )

        response_422 = lambda_handler(event, lambda_context)
        expected_response_422 = '{"statusCode": 422, "header": {"Content-Type": "application/json"}, '
        expected_response_422 += '"body": "{\\"duration_run\\": 0, \\"message\\": \\"Missing required parameter\\", '
        expected_response_422 += '\\"request_id\\": \\"test_invoke_id\\"}", "isBase64Encoded": false}'

        assert response_422 == expected_response_422

    @patch.object(time, "time")
    @patch.object(app, "samexporter_predict")
    @patch.object(app, "get_response")
    @patch.object(app, "get_parsed_bbox_points")
    @patch.object(app, "get_parsed_request_body")
    def test_lambda_handler_200(
            self,
            get_parsed_request_body_mocked,
            get_parsed_bbox_points_mocked,
            get_response_mocked,
            samexporter_predict_mocked,
            time_mocked
    ):
        from src.app import lambda_handler
        from tests import TEST_EVENTS_FOLDER

        time_mocked.return_value = 0
        get_parsed_request_body_mocked.value = {}
        get_parsed_bbox_points_mocked.return_value = {"bbox": "bbox_object", "prompt": "prompt_object", "zoom": 1}

        response_type = "200"
        with open(TEST_EVENTS_FOLDER / "get_response.json") as tst_json_get_response:
            get_response_io = json.load(tst_json_get_response)

        input_200 = {
          "bbox": {
            "ne": {"lat": 38.03932961278458, "lng": 15.36808069832851},
            "sw": {"lat": 37.455509218936974, "lng":  14.632807441554068}
          },
          "prompt": [{
            "type": "point",
            "data": {"lat": 37.0, "lng": 15.0},
            "label": 0
          }],
          "zoom": 10,
          "source_type": "Satellite",
          "debug": True
        }

        samexporter_predict_output = get_response_io[response_type]["input"]
        samexporter_predict_mocked.return_value = samexporter_predict_output
        samexporter_predict_mocked.side_effect = None
        get_response_mocked.return_value = get_response_io[response_type]["output"]

        event = {"body": input_200, "version": 1.0}

        lambda_context = LambdaContext(
            invoke_id="test_invoke_id",
            client_context=None,
            cognito_identity=None,
            epoch_deadline_time_in_ms=time.time()
        )

        response_200 = lambda_handler(event, lambda_context)
        expected_response_200 = get_response_io[response_type]["output"]
        print(f"types: response_200:{type(response_200)}, expected:{type(expected_response_200)}.")
        assert response_200 == expected_response_200
