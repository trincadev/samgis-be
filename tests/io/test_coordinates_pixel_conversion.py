from tests.io.test_utilities import fn_reading_json_inputs_outputs__test


def test_get_latlng2pixel_projection():
    fn_reading_json_inputs_outputs__test(name_fn="get_latlng2pixel_projection")


def test_get_point_latlng_to_pixel_coordinates():
    fn_reading_json_inputs_outputs__test(name_fn="get_point_latlng_to_pixel_coordinates")


def test_get_latlng_to_pixel_coordinates():
    fn_reading_json_inputs_outputs__test(name_fn="get_latlng_to_pixel_coordinates")
