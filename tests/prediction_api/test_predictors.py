import json
import unittest
from unittest.mock import patch

import numpy as np
import shapely
from affine import Affine

from samgis.prediction_api import predictors
from samgis.prediction_api.predictors import samexporter_predict
from tests import TEST_EVENTS_FOLDER


class TestPredictors(unittest.TestCase):
    @patch.object(predictors, "download_extent")
    def test_get_raster_inference(self, download_extent_mocked):
        name_fn = "samexporter_predict"

        with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
            inputs_outputs = json.load(tst_json)
            for k, input_output in inputs_outputs.items():
                input_payload = input_output["input"]
                prompt = input_payload["prompt"]
                model_name = input_payload["model_name"]
                bbox = input_payload["bbox"]
                zoom = input_payload["zoom"]
                print(f"k:{k}.")
                img = np.load(TEST_EVENTS_FOLDER / f"{name_fn}" / k / "img.npy")
                affine_transform = Affine.from_gdal(*input_payload["matrix"])
                download_extent_mocked.return_value = img, affine_transform
                expected_output = input_output["output"]

                output_dict = samexporter_predict(
                    bbox,
                    prompt,
                    zoom,
                    model_name
                )
                len_inference_out = output_dict["n_predictions"]
                geojson = output_dict["geojson"]
                n_shapes_geojson = output_dict["n_shapes_geojson"]

                assert isinstance(geojson, str)
                assert isinstance(n_shapes_geojson, int)
                assert len_inference_out == expected_output["n_predictions"]

                output_geojson = shapely.from_geojson(geojson)
                print("output_geojson::{}.".format(output_geojson))
                assert isinstance(output_geojson, shapely.GeometryCollection)
                assert len(output_geojson.geoms) > 0

    @patch.object(predictors, "get_raster_inference_with_embedding_from_dict")
    @patch.object(predictors, "SegmentAnythingONNX2")
    @patch.object(predictors, "download_extent")
    @patch.object(predictors, "get_vectorized_raster_as_geojson")
    def test_samexporter_predict_mocked(
            self,
            get_vectorized_raster_as_geojson_mocked,
            download_extent_mocked,
            segment_anything_onnx2_mocked,
            get_raster_inference_with_embedding_from_dict_mocked
    ):
        """
        model_instance = SegmentAnythingONNX()
        img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)
        transform = get_affine_transform_from_gdal(matrix)
        mask, n_predictions = get_raster_inference(img, prompt, models_instance, model_name)
        get_vectorized_raster_as_geojson(mask, matrix)
        """
        aff = 1, 2, 3, 4, 5, 6
        segment_anything_onnx2_mocked.return_value = "SegmentAnythingONNX2_instance"
        input_downloaded = np.arange(0, 300, 1).reshape((10, 10, 3))
        download_extent_mocked.return_value = input_downloaded, aff
        mask_output = np.zeros((10, 10))
        mask_output[4:4, 6:6] = 255.0
        get_raster_inference_with_embedding_from_dict_mocked.return_value = mask_output, 1
        get_vectorized_raster_as_geojson_mocked.return_value = {"geojson": "{}", "n_shapes_geojson": 2}
        output = samexporter_predict(
            bbox=[[1, 2], [3, 4]], prompt=[{}], zoom=10, model_name="mobile_sam", source_name="localtest"
        )
        assert output == {"n_predictions": 1, "geojson": "{}", "n_shapes_geojson": 2}
