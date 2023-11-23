import json

from src.io.coordinates_pixel_conversion import _get_latlng2pixel_projection, _get_point_latlng_to_pixel_coordinates, \
    get_latlng_to_pixel_coordinates
from src.utilities.type_hints import LatLngDict
from tests import TEST_EVENTS_FOLDER


def test_get_latlng2pixel_projection():
    name_fn = "get_latlng2pixel_projection"

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}")
            current_input = input_output["input"]
            latlng_input = LatLngDict.model_validate(current_input["latlng"])
            output = _get_latlng2pixel_projection(latlng_input)
            assert output == input_output["output"]


def test_get_point_latlng_to_pixel_coordinates():
    name_fn = "get_point_latlng_to_pixel_coordinates"

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}")
            current_input = input_output["input"]
            latlng_input = LatLngDict.model_validate(current_input["latlng"])
            output = _get_point_latlng_to_pixel_coordinates(latlng=latlng_input, zoom=current_input["zoom"])
            assert output == input_output["output"]


def test_get_latlng_to_pixel_coordinates():
    name_fn = "get_latlng_to_pixel_coordinates"

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}")
            current_input = input_output["input"]
            zoom = current_input["zoom"]
            latlng_origin_ne = LatLngDict.model_validate(current_input["latlng_origin_ne"])
            latlng_origin_sw = LatLngDict.model_validate(current_input["latlng_origin_sw"])
            latlng_current_point = LatLngDict.model_validate(current_input["latlng_current_point"])
            output = get_latlng_to_pixel_coordinates(
                latlng_origin_ne=latlng_origin_ne,
                latlng_origin_sw=latlng_origin_sw,
                latlng_current_point=latlng_current_point,
                zoom=zoom,
                k=k
            )
            assert output == input_output["output"]
