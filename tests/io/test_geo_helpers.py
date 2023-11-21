import json
import numpy as np
import shapely

from tests import TEST_EVENTS_FOLDER


def test_get_vectorized_raster_as_geojson():
    from src.io.geo_helpers import get_vectorized_raster_as_geojson

    name_fn = "samexporter_predict"

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            print(f"k:{k}.")
            mask = np.load(TEST_EVENTS_FOLDER / name_fn / k / "mask.npy")

            output = get_vectorized_raster_as_geojson(mask=mask, matrix=input_output["input"]["matrix"])
            assert output["n_shapes_geojson"] == input_output["output"]["n_shapes_geojson"]
            output_geojson = shapely.from_geojson(output["geojson"])
            expected_output_geojson = shapely.from_geojson(input_output["output"]["geojson"])
            assert shapely.equals_exact(output_geojson, expected_output_geojson, tolerance=0.000006)
