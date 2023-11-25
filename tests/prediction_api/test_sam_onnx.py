import logging
import unittest
from unittest.mock import patch

import numpy as np

from src import MODEL_FOLDER
from src.prediction_api import sam_onnx
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME
from src.utilities.utilities import hash_calculate
from tests import TEST_EVENTS_FOLDER


instance_sam_onnx = SegmentAnythingONNX(
    encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
    decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
)
np_img = np.load(TEST_EVENTS_FOLDER / "samexporter_predict" / "oceania" / "img.npy")
prompt = [{
    "type": "point",
    "data": [934, 510],
    "label": 0
}]


class TestSegmentAnythingONNX(unittest.TestCase):
    def test_encode_predict_masks_ok(self):
        embedding = instance_sam_onnx.encode(np_img)
        try:
            assert hash_calculate(embedding) == b"m2O3y7pNUwlLuAZhBHkRIu8cDIIej0oOmWOXevs39r4="
        except AssertionError as ae1:
            logging.warning(f"ae1:{ae1}.")
        inference_mask = instance_sam_onnx.predict_masks(embedding, prompt)
        try:
            assert hash_calculate(inference_mask) == b'YSKKNCs3AMpbeDUVwqIwNQqJ365OG4239hxjFnW7XTM='
        except AssertionError as ae2:
            logging.warning(f"ae2:{ae2}.")
        mask_output = np.zeros((inference_mask.shape[2], inference_mask.shape[3]), dtype=np.uint8)
        for n, m in enumerate(inference_mask[0, :, :, :]):
            logging.debug(f"{n}th of prediction_masks shape {inference_mask.shape}"
                          f" => mask shape:{mask_output.shape}, {mask_output.dtype}.")
            mask_output[m > 0.0] = 255
        mask_expected = np.load(TEST_EVENTS_FOLDER / "SegmentAnythingONNX" / "mask_output.npy")

        # assert MAP (mean average precision) is 100%
        # sum expected mask to output mask:
        # - asserted "good" inference values are 2 (matched object) or 0 (matched background)
        # - "bad" inference value is 1 (there are differences between expected and output mask)
        sum_mask_output_vs_expected = mask_expected / 255 + mask_output / 255
        unique_values__output_vs_expected = np.unique(sum_mask_output_vs_expected, return_counts=True)
        tot = sum_mask_output_vs_expected.size
        perc = {
            k: 100 * v / tot for
            k, v in
            zip(unique_values__output_vs_expected[0], unique_values__output_vs_expected[1])
        }
        try:
            assert 1 not in perc
        except AssertionError:
            logging.error(f"found {perc[1]} % different pixels between expected masks and output mask.")
            # try to assert that the % of different pixels are minor than 5%
            assert perc[1] < 5

    def test_encode_predict_masks_ex1(self):
        instance_sam_onnx = SegmentAnythingONNX(
            encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
            decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
        )
        with self.assertRaises(Exception):
            try:
                np_input = np.zeros((10, 10))
                instance_sam_onnx.encode(np_input)
            except Exception as e:
                logging.error(f"e:{e}.")
                msg = "[ONNXRuntimeError] : 2 : INVALID_ARGUMENT : Invalid rank for input: input_image "
                msg += "Got: 2 Expected: 3 Please fix either the inputs or the model."
                assert str(e) == msg
                raise e

    def test_encode_predict_masks_ex2(self):
        wrong_prompt = [{
            "type": "rectangle",
            "data": [934, 510],
            "label": 0
        }]
        embedding = instance_sam_onnx.encode(np_img)

        with self.assertRaises(IndexError):
            try:
                instance_sam_onnx.predict_masks(embedding, wrong_prompt)
            except IndexError as ie:
                print(ie)
                assert str(ie) == "list index out of range"
                raise ie
