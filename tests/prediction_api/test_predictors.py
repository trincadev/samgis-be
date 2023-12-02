import json
from unittest.mock import patch

import numpy as np

from src.prediction_api import predictors
from src.prediction_api.predictors import get_raster_inference, samexporter_predict
from tests import TEST_EVENTS_FOLDER


@patch.object(predictors, "SegmentAnythingONNX")
def test_get_raster_inference(segment_anything_onnx_mocked):
    name_fn = "samexporter_predict"

    with open(TEST_EVENTS_FOLDER / f"{name_fn}.json") as tst_json:
        inputs_outputs = json.load(tst_json)
        for k, input_output in inputs_outputs.items():
            model_mocked = segment_anything_onnx_mocked()

            img = np.load(TEST_EVENTS_FOLDER / f"{name_fn}" / k / "img.npy")
            inference_out = np.load(TEST_EVENTS_FOLDER / f"{name_fn}" / k / "inference_out.npy")
            mask = np.load(TEST_EVENTS_FOLDER / f"{name_fn}" / k / "mask.npy")
            prompt = input_output["input"]["prompt"]
            model_name = input_output["input"]["model_name"]

            model_mocked.embed.return_value = np.array(img)
            model_mocked.embed.side_effect = None
            model_mocked.predict_masks.return_value = inference_out
            model_mocked.predict_masks.side_effect = None
            print(f"k:{k}.")
            output_mask, len_inference_out = get_raster_inference(
                img=img,
                prompt=prompt,
                models_instance=model_mocked,
                model_name=model_name
            )
            assert np.array_equal(output_mask, mask)
            assert len_inference_out == input_output["output"]["n_predictions"]


@patch.object(predictors, "get_raster_inference")
@patch.object(predictors, "SegmentAnythingONNX")
@patch.object(predictors, "download_extent")
@patch.object(predictors, "get_vectorized_raster_as_geojson")
def test_samexporter_predict(
        get_vectorized_raster_as_geojson_mocked,
        download_extent_mocked,
        segment_anything_onnx_mocked,
        get_raster_inference_mocked
):
    """
    model_instance = SegmentAnythingONNX()
    img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)
    transform = get_affine_transform_from_gdal(matrix)
    mask, n_predictions = get_raster_inference(img, prompt, models_instance, model_name)
    get_vectorized_raster_as_geojson(mask, matrix)
    """
    aff = 1, 2, 3, 4, 5, 6
    segment_anything_onnx_mocked.return_value = "SegmentAnythingONNX_instance"
    download_extent_mocked.return_value = np.zeros((10, 10)), aff
    get_raster_inference_mocked.return_value = np.ones((10, 10)), 1
    get_vectorized_raster_as_geojson_mocked.return_value = {"geojson": "{}", "n_shapes_geojson": 2}
    output = samexporter_predict(bbox=[[1, 2], [3, 4]], prompt=[{}], zoom=10, model_name="fastsam")
    assert output == {"n_predictions": 1, "geojson": "{}", "n_shapes_geojson": 2}
