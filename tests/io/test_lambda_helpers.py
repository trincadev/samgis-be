import json

from src.io.lambda_helpers import get_parsed_bbox_points, get_parsed_request_body
from tests import TEST_EVENTS_FOLDER


def test_get_parsed_bbox_points():
    with open(TEST_EVENTS_FOLDER / "get_parsed_bbox_points.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            raw_body = get_parsed_request_body(**input_output["input"])
            output = get_parsed_bbox_points(raw_body)
            assert output == input_output["output"]
