import json

from src.io.lambda_helpers import get_parsed_bbox_points, get_parsed_request_body
from src.utilities.type_hints import RawRequestInput
from src.utilities.utilities import base64_encode
from tests import TEST_EVENTS_FOLDER


def test_get_parsed_bbox_points():
    with open(TEST_EVENTS_FOLDER / "get_parsed_bbox_points.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            raw_body = get_parsed_request_body(**input_output["input"])
            output = get_parsed_bbox_points(raw_body)
            assert output == input_output["output"]


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
    assert output == RawRequestInput.model_validate(input_event["event"])

    input_event_str = json.dumps(input_event["event"])
    output = get_parsed_request_body(input_event_str)
    assert output == RawRequestInput.model_validate(expected_output_dict)

    event = {"body": base64_encode(input_event_str).decode("utf-8")}
    output = get_parsed_request_body(event)
    assert output == RawRequestInput.model_validate(expected_output_dict)
