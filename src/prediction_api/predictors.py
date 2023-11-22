# Press the green button in the gutter to run the script.
import json
import tempfile

import numpy as np

from src import app_logger, MODEL_FOLDER
from src.io.geo_helpers import get_vectorized_raster_as_geojson, get_affine_transform_from_gdal
from src.io.tms2geotiff import download_extent
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME, DEFAULT_TMS
from src.utilities.serialize import serialize


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

        app_logger.info(f'tile_source: {DEFAULT_TMS}!')
        pt0, pt1 = bbox
        app_logger.info(f"downloading geo-referenced raster with bbox {bbox}, zoom {zoom}.")
        img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)
        app_logger.info(f"img type {type(img)} with shape/size:{img.size}, matrix:{matrix}.")

        with tempfile.NamedTemporaryFile(mode='w', prefix=f"matrix_", delete=False) as temp_f1:
            json.dump({"matrix": serialize(matrix)}, temp_f1)

        transform = get_affine_transform_from_gdal(matrix)
        app_logger.debug(f"transform to consume with rasterio.shapes: {type(transform)}, {transform}.")

        mask, n_predictions = get_raster_inference(img, prompt, models_instance, model_name)
        app_logger.info(f"created {n_predictions} masks, preparing conversion to geojson...")
        return {
            "n_predictions": n_predictions,
            **get_vectorized_raster_as_geojson(mask, matrix)
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
    try:
        with tempfile.NamedTemporaryFile(mode='w', prefix=f"get_raster_inference__img_", delete=False) as temp_f0:
            np.save(str(temp_f0.file.name), np_img)
    except Exception as e_save:
        app_logger.error(f"e_save:{e_save}.")
        raise e_save
    app_logger.info(f"instantiated model {model_name}, ENCODER {MODEL_ENCODER_NAME}, "
                    f"DECODER {MODEL_DECODER_NAME} from {MODEL_FOLDER}: Creating embedding...")
    embedding = models_instance.encode(np_img)
    app_logger.debug(f"embedding created, running predict_masks with prompt {prompt}...")
    inference_out = models_instance.predict_masks(embedding, prompt)
    len_inference_out = len(inference_out[0, :, :, :])
    app_logger.info(f"Created {len_inference_out} prediction_masks,"
                    f"shape:{inference_out.shape}, dtype:{inference_out.dtype}.")
    mask = np.zeros((inference_out.shape[2], inference_out.shape[3]), dtype=np.uint8)
    for n, m in enumerate(inference_out[0, :, :, :]):
        app_logger.debug(f"{n}th of prediction_masks shape {inference_out.shape}"
                         f" => mask shape:{mask.shape}, {mask.dtype}.")
        mask[m > 0.0] = 255
    try:
        with tempfile.NamedTemporaryFile(mode='w', prefix=f"get_raster_inference__mask_", delete=False) as temp_f1:
            np.save(temp_f1.file.name, mask)
        with tempfile.NamedTemporaryFile(mode='w', prefix=f"get_raster_inference__inference_out_", delete=False) as temp_f2:
            np.save(temp_f2.file.name, inference_out)
    except Exception as e_save1:
        app_logger.error(f"e_save1:{e_save1}.")
        raise e_save1
    return mask, len_inference_out
