import json
import unittest

import numpy as np
import shapely

from src.io.geo_helpers import load_affine_transformation_from_matrix
from tests import TEST_EVENTS_FOLDER


class TestGeoHelpers(unittest.TestCase):
    def test_load_affine_transformation_from_matrix(self):
        name_fn = "samexporter_predict"

        expected_output = {
            'europe': (
                1524458.6551710723, 0.0, 152.87405657035242, 4713262.318571913, -762229.3275855362, -2356860.470370812
            ),
            'north_america': (
                -13855281.495084189, 0.0, 1222.9924525628194, 6732573.451358326, 6927640.747542094, -3368121.214358007
            ),
            'oceania': (
                7269467.138033403, 0.0, 9783.93962050256, -166326.9735485418, -3634733.5690167015, 68487.57734351706
            ),
            'south_america': (
                -7922544.351904369, 0.0, 305.74811314070394, -5432228.234830927, 3961272.1759521845, 2715655.4952457524
            )}

        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            for k, input_output in inputs_outputs.items():
                print(f"k:{k}.")

                output = load_affine_transformation_from_matrix(input_output["input"]["matrix"])
                assert output.to_shapely() == expected_output[k]

    def test_load_affine_transformation_from_matrix_value_error(self):
        name_fn = "samexporter_predict"
        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            with self.assertRaises(ValueError):
                try:
                    io_value_error = inputs_outputs["europe"]["input"]["matrix"][:5]
                    load_affine_transformation_from_matrix(io_value_error)
                except ValueError as ve:
                    print(f"ve:{ve}.")
                    self.assertEqual(str(ve), "Expected 6 coefficients, found 5; argument type: <class 'list'>.")
                    raise ve

    def test_load_affine_transformation_from_matrix_exception(self):
        name_fn = "samexporter_predict"
        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            with self.assertRaises(Exception):
                try:
                    io_exception = inputs_outputs["europe"]["input"]["matrix"]
                    io_exception[0] = "ciao"
                    load_affine_transformation_from_matrix(io_exception)
                except Exception as e:
                    print(f"e:{e}.")
                    self.assertEqual(str(e), "exception:could not convert string to float: 'ciao', "
                                             "check https://github.com/rasterio/affine project for updates")
                    raise e

    def test_get_vectorized_raster_as_geojson_ok(self):
        from rasterio.transform import Affine
        from src.io.geo_helpers import get_vectorized_raster_as_geojson

        name_fn = "samexporter_predict"

        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            for k, input_output in inputs_outputs.items():
                print(f"k:{k}.")
                mask = np.load(TEST_EVENTS_FOLDER / name_fn / k / "mask.npy")

                transform = Affine.from_gdal(*input_output["input"]["matrix"])
                output = get_vectorized_raster_as_geojson(mask=mask, transform=transform)
                assert output["n_shapes_geojson"] == input_output["output"]["n_shapes_geojson"]
                output_geojson = shapely.from_geojson(output["geojson"])
                expected_output_geojson = shapely.from_geojson(input_output["output"]["geojson"])
                assert shapely.equals_exact(output_geojson, expected_output_geojson, tolerance=0.000006)

    def test_get_vectorized_raster_as_geojson_fail(self):
        from src.io.geo_helpers import get_vectorized_raster_as_geojson

        name_fn = "samexporter_predict"

        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            for k, input_output in inputs_outputs.items():
                print(f"k:{k}.")
                mask = np.load(TEST_EVENTS_FOLDER / name_fn / k / "mask.npy")

                # Could be also another generic Exception, here we intercept TypeError caused by wrong matrix input on
                # rasterio.Affine.from_gdal() wrapped by get_affine_transform_from_gdal()
                with self.assertRaises(IndexError):
                    try:
                        wrong_matrix = 1.0,
                        get_vectorized_raster_as_geojson(mask=mask, transform=wrong_matrix)
                    except IndexError as te:
                        print(f"te:{te}.")
                        self.assertEqual(str(te), 'tuple index out of range')
                        raise te
