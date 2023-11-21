import json

from src.io.coordinates_pixel_conversion import get_latlng2pixel_projection, get_point_latlng_to_pixel_coordinates, \
    get_latlng_to_pixel_coordinates
from src.io.lambda_helpers import get_parsed_bbox_points

from tests import TEST_EVENTS_FOLDER


names_fn_dict = {
    "get_latlng2pixel_projection": get_latlng2pixel_projection,
    "get_point_latlng_to_pixel_coordinates": get_point_latlng_to_pixel_coordinates,
    "get_latlng_to_pixel_coordinates": get_latlng_to_pixel_coordinates,
    "get_parsed_bbox_points": get_parsed_bbox_points
}


def fn_reading_json_inputs_outputs__test(name_fn):
    fn = names_fn_dict[name_fn]

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            output = fn(**input_output["input"])
            assert output == input_output["output"]
