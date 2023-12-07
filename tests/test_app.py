import json
import time
import unittest
from unittest.mock import patch

from awslambdaric.lambda_context import LambdaContext

from src import app
from src.io import lambda_helpers
from tests.local_tiles_http_server import LocalTilesHttpServer


class TestAppFailures(unittest.TestCase):
    @patch.object(time, "time")
    @patch.object(app, "samexporter_predict")
    @patch.object(app, "get_parsed_bbox_points")
    @patch.object(app, "get_parsed_request_body")
    def test_lambda_handler_500(
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
        expected_response_500 = '{"statusCode": 500, "header": {"Content-Type": "application/json"}, '
        expected_response_500 += '"body": "{\\"duration_run\\": 0, \\"message\\": \\"Internal server error\\", '
        expected_response_500 += '\\"request_id\\": \\"test_invoke_id\\"}", "isBase64Encoded": false}'

        assert lambda_handler(event, lambda_context) == expected_response_500

    @patch.object(time, "time")
    @patch.object(app, "get_parsed_request_body")
    def test_lambda_handler_400(self, get_parsed_request_body_mocked, time_mocked):
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

        assert lambda_handler(event, lambda_context) == (
            '{"statusCode": 400, "header": {"Content-Type": "application/json"}, '
            '"body": "{\\"duration_run\\": 0, \\"message\\": \\"Bad Request\\", '
            '\\"request_id\\": \\"test_invoke_id\\"}", "isBase64Encoded": false}')

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
    def test_lambda_handler_200_mocked(
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
                "sw": {"lat": 37.455509218936974, "lng": 14.632807441554068}
            },
            "prompt": [{
                "type": "point",
                "data": {"lat": 37.0, "lng": 15.0},
                "label": 0
            }],
            "zoom": 10,
            "source_type": "OpenStreetMap.Mapnik",
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

    @patch.object(lambda_helpers, "get_url_tile")
    def test_lambda_handler_200_real_single_multi_point(self, get_url_tile_mocked):
        import xyzservices
        import shapely

        from src.app import lambda_handler
        from tests import LOCAL_URL_TILE, TEST_EVENTS_FOLDER

        local_tile_provider = xyzservices.TileProvider(name="local_tile_provider", url=LOCAL_URL_TILE, attribution="")
        get_url_tile_mocked.return_value = local_tile_provider
        fn_name = "lambda_handler"
        invoke_id = "test_invoke_id"

        for json_filename in [
            "single_point",
            "multi_prompt",
            "single_rectangle"
        ]:
            with open(TEST_EVENTS_FOLDER / f"{fn_name}_{json_filename}.json") as tst_json:
                inputs_outputs = json.load(tst_json)
                lambda_context = LambdaContext(
                    invoke_id=invoke_id,
                    client_context=None,
                    cognito_identity=None,
                    epoch_deadline_time_in_ms=time.time()
                )
                expected_response_dict = inputs_outputs["output"]
                listen_port = 8000
                expected_response_body = json.loads(expected_response_dict["body"])

                with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
                    input_event = inputs_outputs["input"]
                    input_event_body = json.loads(input_event["body"])
                    input_event["body"] = json.dumps(input_event_body)
                    response = lambda_handler(event=input_event, context=lambda_context)

                response_dict = json.loads(response)
                assert response_dict["statusCode"] == 200
                body_dict = json.loads(response_dict["body"])
                assert body_dict["n_predictions"] == 1
                assert body_dict["request_id"] == invoke_id
                assert body_dict["message"] == "ok"
                assert body_dict["n_shapes_geojson"] == expected_response_body["n_shapes_geojson"]

                output_geojson = shapely.from_geojson(body_dict["geojson"])
                print("output_geojson::", type(output_geojson))
                assert isinstance(output_geojson, shapely.GeometryCollection)
                assert len(output_geojson.geoms) == expected_response_body["n_shapes_geojson"]

    def test_debug(self):
        from src.app import lambda_handler

        input_event = {
            'bbox': {
                'ne': {'lat': 46.302592089330524, 'lng': 9.49493408203125},
                'sw': {'lat': 46.14011755129237, 'lng': 9.143371582031252}},
            'prompt': [
                {'id': 166, 'type': 'point', 'data': {'lat': 46.18244521829928, 'lng': 9.418544769287111}, 'label': 1}
            ],
            'zoom': 12, 'source_type': 'OpenStreetMap'
        }
        lambda_context = LambdaContext(
            invoke_id="test_invoke_id",
            client_context=None,
            cognito_identity=None,
            epoch_deadline_time_in_ms=time.time()
        )
        response = lambda_handler(event=input_event, context=lambda_context)
        print(response)
