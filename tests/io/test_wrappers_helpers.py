import json
import time
import unittest

from http import HTTPStatus
from unittest.mock import patch

from samgis.io import wrappers_helpers
from samgis.io.wrappers_helpers import get_parsed_bbox_points, get_parsed_request_body, get_response
from samgis.utilities.type_hints import ApiRequestBody
from tests import TEST_EVENTS_FOLDER


class WrappersHelpersTest(unittest.TestCase):
    @patch.object(time, "time")
    def test_get_response(self, time_mocked):
        time_diff = 108
        end_run = 1000
        time_mocked.return_value = end_run
        start_time = end_run - time_diff
        aws_request_id = "test_invoke_id"

        with open(TEST_EVENTS_FOLDER / "get_response.json") as tst_json:
            inputs_outputs = json.load(tst_json)

        response_type = "200"
        body_response = inputs_outputs[response_type]["input"]
        output = get_response(HTTPStatus.OK.value, start_time, aws_request_id, body_response)
        assert json.loads(output) == inputs_outputs[response_type]["output"]

        response_type = "400"
        response_400 = get_response(HTTPStatus.BAD_REQUEST.value, start_time, aws_request_id, {})
        assert response_400 == inputs_outputs[response_type]["output"]

        response_type = "422"
        response_422 = get_response(HTTPStatus.UNPROCESSABLE_ENTITY.value, start_time, aws_request_id, {})
        assert response_422 == inputs_outputs[response_type]["output"]

        response_type = "500"
        response_500 = get_response(HTTPStatus.INTERNAL_SERVER_ERROR.value, start_time, aws_request_id, {})
        assert response_500 == inputs_outputs[response_type]["output"]

    @staticmethod
    def test_get_parsed_bbox_points():
        with open(TEST_EVENTS_FOLDER / "get_parsed_bbox_prompts_single_point.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            for k, input_output in inputs_outputs.items():
                print(f"k:{k}.")
                raw_body = get_parsed_request_body(**input_output["input"])
                output = get_parsed_bbox_points(raw_body)
                assert output == input_output["output"]

    @staticmethod
    def test_get_parsed_bbox_other_inputs():
        for json_filename in ["single_rectangle", "multi_prompt"]:
            with open(TEST_EVENTS_FOLDER / f"get_parsed_bbox_prompts_{json_filename}.json") as tst_json:
                inputs_outputs = json.load(tst_json)
                parsed_input = ApiRequestBody.model_validate(inputs_outputs["input"])
                output = get_parsed_bbox_points(parsed_input)
                assert output == inputs_outputs["output"]

    @staticmethod
    def test_get_parsed_request_body():
        from samgis_core.utilities.utilities import base64_encode

        input_event = {
            "event": {
                "bbox": {
                    "ne": {"lat": 38.03932961278458, "lng": 15.36808069832851},
                    "sw": {"lat": 37.455509218936974, "lng": 14.632807441554068}
                },
                "prompt": [{"type": "point", "data": {"lat": 37.0, "lng": 15.0}, "label": 0}],
                "zoom": 10, "source_type": "OpenStreetMap.Mapnik", "debug": True
            }
        }
        expected_output_dict = {
            "bbox": {
                "ne": {"lat": 38.03932961278458, "lng": 15.36808069832851},
                "sw": {"lat": 37.455509218936974, "lng": 14.632807441554068}
            },
            "prompt": [{"type": "point", "data": {"lat": 37.0, "lng": 15.0}, "label": 0}],
            "zoom": 10, "source_type": "OpenStreetMap.Mapnik", "debug": True
        }
        output = get_parsed_request_body(input_event["event"])
        assert output == ApiRequestBody.model_validate(input_event["event"])

        input_event_str = json.dumps(input_event["event"])
        output = get_parsed_request_body(input_event_str)
        assert output == ApiRequestBody.model_validate(expected_output_dict)

        event = {"body": base64_encode(input_event_str).decode("utf-8")}
        output = get_parsed_request_body(event)
        assert output == ApiRequestBody.model_validate(expected_output_dict)

    @patch.object(wrappers_helpers, "providers")
    def test_get_url_tile(self, providers_mocked):
        import xyzservices
        from samgis.io.wrappers_helpers import get_url_tile

        from tests import LOCAL_URL_TILE

        local_tile_provider = xyzservices.TileProvider(name="local_tile_provider", url=LOCAL_URL_TILE, attribution="")
        expected_output = {'name': 'local_tile_provider', 'url': LOCAL_URL_TILE, 'attribution': ''}
        providers_mocked.query_name.return_value = local_tile_provider
        assert get_url_tile("OpenStreetMap") == expected_output

        local_url = 'http://localhost:8000/{parameter}/{z}/{x}/{y}.png'
        local_tile_provider = xyzservices.TileProvider(
            name="local_tile_provider_param", url=local_url, attribution="", parameter="lamda_handler"
        )
        providers_mocked.query_name.return_value = local_tile_provider
        assert get_url_tile("OpenStreetMap.HOT") == {
            "parameter": "lamda_handler", 'name': 'local_tile_provider_param', 'url': local_url, 'attribution': ''
        }

    @staticmethod
    def test_get_url_tile_real():
        from samgis.io.wrappers_helpers import get_url_tile

        assert get_url_tile("OpenStreetMap") == {
            'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'max_zoom': 19,
            'html_attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            'attribution': '(C) OpenStreetMap contributors',
            'name': 'OpenStreetMap.Mapnik'}

        html_attribution_hot = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, '
        html_attribution_hot += 'Tiles style by <a href="https://www.hotosm.org/" target="_blank">Humanitarian '
        html_attribution_hot += 'OpenStreetMap Team</a> hosted by <a href="https://openstreetmap.fr/" target="_blank">'
        html_attribution_hot += 'OpenStreetMap France</a>'
        attribution_hot = '(C) OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by '
        attribution_hot += 'OpenStreetMap France'
        assert get_url_tile("OpenStreetMap.HOT") == {
            'url': 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', 'max_zoom': 19,
            'html_attribution': html_attribution_hot, 'attribution': attribution_hot, 'name': 'OpenStreetMap.HOT'
        }
