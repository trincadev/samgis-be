import json
import time
from http import HTTPStatus
from unittest.mock import patch
from src.io.lambda_helpers import get_parsed_bbox_points, get_parsed_request_body, get_response
from src.utilities.type_hints import ApiRequestBody
from src.utilities import utilities
from tests import TEST_EVENTS_FOLDER


@patch.object(time, "time")
def test_get_response(time_mocked):
    time_diff = 108
    end_run = 1000
    time_mocked.return_value = end_run
    start_time = end_run-time_diff
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


def test_get_parsed_bbox_points():
    with open(TEST_EVENTS_FOLDER / "get_parsed_bbox_prompts_single_point.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            raw_body = get_parsed_request_body(**input_output["input"])
            output = get_parsed_bbox_points(raw_body)
            assert output == input_output["output"]


def test_get_parsed_bbox_other_inputs():
    for json_filename in ["single_rectangle", "multi_prompt"]:
        with open(TEST_EVENTS_FOLDER / f"get_parsed_bbox_prompts_{json_filename}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            parsed_input = ApiRequestBody.model_validate(inputs_outputs["input"])
            output = get_parsed_bbox_points(parsed_input)
            assert output == inputs_outputs["output"]


def test_get_parsed_request_body():
    input_event = {
        "event": {
            "bbox": {
                "ne": {"lat": 38.03932961278458, "lng": 15.36808069832851},
                "sw": {"lat": 37.455509218936974, "lng": 14.632807441554068}
            },
            "prompt": [{"type": "point", "data": {"lat": 37.0, "lng": 15.0}, "label": 0}],
            "zoom": 10, "source_type": "Satellite", "debug": True
        }
    }
    expected_output_dict = {
        "bbox": {
            "ne": {"lat": 38.03932961278458, "lng": 15.36808069832851},
            "sw": {"lat": 37.455509218936974, "lng": 14.632807441554068}
        },
        "prompt": [{"type": "point", "data": {"lat": 37.0, "lng": 15.0}, "label": 0}],
        "zoom": 10, "source_type": "Satellite", "debug": True
    }
    output = get_parsed_request_body(input_event["event"])
    assert output == ApiRequestBody.model_validate(input_event["event"])

    input_event_str = json.dumps(input_event["event"])
    output = get_parsed_request_body(input_event_str)
    assert output == ApiRequestBody.model_validate(expected_output_dict)

    event = {"body": utilities.base64_encode(input_event_str).decode("utf-8")}
    output = get_parsed_request_body(event)
    assert output == ApiRequestBody.model_validate(expected_output_dict)


def test_get_url_tile():
    from src.io.lambda_helpers import get_url_tile
    from src.utilities.constants import DEFAULT_TMS

    assert get_url_tile("OpenStreetMap") == DEFAULT_TMS
    assert get_url_tile("OpenStreetMap.HOT") == 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'
