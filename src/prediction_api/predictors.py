# Press the green button in the gutter to run the script.
import tempfile
from pathlib import Path

import numpy as np

from src import app_logger, MODEL_FOLDER
from src.io.geo_helpers import get_vectorized_raster_as_geojson
from src.io.tms2geotiff import save_geotiff_gdal, download_extent
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME, DEFAULT_TMS


models_dict = {"fastsam": {"instance": None}}


def samexporter_predict(bbox, prompt: list[dict], zoom: float, model_name: str = "fastsam") -> dict:
    try:
        if models_dict[model_name]["instance"] is None:
            app_logger.info(f"missing instance model {model_name}, instantiating it now!")
            model_instance = SegmentAnythingONNX(
                encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
                decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
            )
            models_dict[model_name]["instance"] = model_instance
        app_logger.debug(f"using a {model_name} instance model...")
        models_instance = models_dict[model_name]["instance"]

        with tempfile.TemporaryDirectory() as input_tmp_dir:
            app_logger.info(f'tile_source: {DEFAULT_TMS}!')
            pt0, pt1 = bbox
            app_logger.info("downloading...")
            img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)
            app_logger.debug(f"img type {type(img)} with shape/size:{img.size}, matrix:{matrix}.")

            pt0, pt1 = bbox
            rio_output = str(Path(input_tmp_dir) / f"downloaded_rio_{pt0[0]}_{pt0[1]}_{pt1[0]}_{pt1[1]}.tif")
            app_logger.debug(f"saving downloaded image as geotiff using matrix {matrix} to {rio_output}...")
            save_geotiff_gdal(img, rio_output, matrix)
            app_logger.info(f"saved downloaded geotiff image to {rio_output}, preparing inference...")

            mask, prediction_masks = get_raster_inference(img, prompt, models_instance, model_name)
            n_predictions = len(prediction_masks)
            app_logger.info(f"created {n_predictions} masks, preparing conversion to geojson...")
            return {
                "n_predictions": n_predictions,
                **get_vectorized_raster_as_geojson(rio_output, mask)
            }
    except ImportError as e_import_module:
        app_logger.error(f"Error trying import module:{e_import_module}.")


def get_raster_inference(img, prompt, models_instance, model_name):
    np_img = np.array(img)
    app_logger.info(f"img type {type(np_img)}, prompt:{prompt}.")
    app_logger.debug(f"onnxruntime input shape/size (shape if PIL) {np_img.size}.")
    try:
        app_logger.debug(f"onnxruntime input shape (NUMPY) {np_img.shape}.")
    except Exception as e_shape:
        app_logger.error(f"e_shape:{e_shape}.")
    app_logger.info(f"instantiated model {model_name}, ENCODER {MODEL_ENCODER_NAME}, "
                    f"DECODER {MODEL_DECODER_NAME} from {MODEL_FOLDER}: Creating embedding...")
    embedding = models_instance.encode(np_img)
    app_logger.debug(f"embedding created, running predict_masks with prompt {prompt}...")
    inference_out = models_instance.predict_masks(embedding, prompt)
    app_logger.info(f"Created {len(inference_out)} prediction_masks,"
                    f"shape:{inference_out.shape}, dtype:{inference_out.dtype}.")
    mask = np.zeros((inference_out.shape[2], inference_out.shape[3]), dtype=np.uint8)
    for n, m in enumerate(inference_out[0, :, :, :]):
        app_logger.debug(f"{n}th of prediction_masks shape {inference_out.shape}"
                         f" => mask shape:{mask.shape}, {mask.dtype}.")
        mask[m > 0.0] = 255
    return mask, inference_out
