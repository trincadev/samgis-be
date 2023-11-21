import json
from unittest.mock import patch

import numpy as np

from src.prediction_api import sam_onnx
from src.prediction_api.predictors import get_raster_inference
from tests import TEST_EVENTS_FOLDER


@patch.object(sam_onnx, "SegmentAnythingONNX")
def test_get_raster_inference(
    segment_anything_onnx_mocked
):
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
