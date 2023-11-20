import json
from unittest import TestCase

from src.io.coordinates_pixel_conversion import get_latlng2pixel_projection, get_point_latlng_to_pixel_coordinates
from tests import TEST_EVENTS_FOLDER


names_fn_dict = {
    "get_latlng2pixel_projection": get_latlng2pixel_projection,
    "get_point_latlng_to_pixel_coordinates": get_point_latlng_to_pixel_coordinates
}


def test_fn_reading_json_inputs_outputs(name_fn):
    fn = names_fn_dict[name_fn]

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            output = fn(**input_output["input"])
            assert output == input_output["output"]


class Test(TestCase):
    def test_get_latlng2pixel_projection(self):
        test_fn_reading_json_inputs_outputs("get_latlng2pixel_projection")

    def test_get_point_latlng_to_pixel_coordinates(self):
        test_fn_reading_json_inputs_outputs("get_point_latlng_to_pixel_coordinates")

    # def test_get_latlng_to_pixel_coordinates(self):
    #     self.fail()
    #
    # def test_pixel_coordinate(self):
    #     self.fail()
