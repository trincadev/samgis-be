# Press the green button in the gutter to run the script.
import os
import numpy as np

from src import app_logger, MODEL_FOLDER
from src.io.tms2geotiff import download_extent
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import ROOT, MODEL_ENCODER_NAME, ZOOM, SOURCE_TYPE, DEFAULT_TMS, MODEL_DECODER_NAME
from src.utilities.serialize import serialize
from src.utilities.type_hints import input_float_tuples
from src.utilities.utilities import get_system_info


def zip_arrays(arr1, arr2):
    arr1_list = arr1.tolist()
    arr2_list = arr2.tolist()
    # return {serialize(k): serialize(v) for k, v in zip(arr1_list, arr2_list)}
    d = {}
    for n1, n2 in enumerate(zip(arr1_list, arr2_list)):
        app_logger.info(f"n1:{n1}, type {type(n1)}, n2:{n2}, type {type(n2)}.")
        n1f = str(n1)
        n2f = str(n2)
        app_logger.info(f"n1:{n1}=>{n1f}, n2:{n2}=>{n2f}.")
        d[n1f] = n2f
    app_logger.info(f"zipped dict:{d}.")
    return d


def samexporter_predict(bbox: input_float_tuples, prompt: list[dict], zoom: float = ZOOM) -> dict:
    import tempfile

    try:
        os.environ['MPLCONFIGDIR'] = ROOT
        get_system_info()
    except Exception as e:
        app_logger.error(f"Error while setting 'MPLCONFIGDIR':{e}.")

    with tempfile.NamedTemporaryFile(prefix=f"{SOURCE_TYPE}_", suffix=".tif", dir=ROOT) as image_input_tmp:
        for coord in bbox:
            app_logger.info(f"bbox coord:{coord}, type:{type(coord)}.")
        app_logger.info(f"start download_extent using bbox:{bbox}, type:{type(bbox)}, download image...")

        pt0 = bbox[0]
        pt1 = bbox[1]
        img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)

        app_logger.info(f"img type {type(img)}, matrix type {type(matrix)}.")
        np_img = np.array(img)
        app_logger.info(f"np_img type {type(np_img)}.")
        app_logger.info(f"np_img dtype {np_img.dtype}, shape {np_img.shape}.")
        app_logger.info(f"geotiff created with size/shape {img.size} and transform matrix {str(matrix)}, start to initialize SamGeo instance:")
        app_logger.info(f"use ENCODER model {MODEL_ENCODER_NAME} from {MODEL_FOLDER})...")
        app_logger.info(f"use DECODER model {MODEL_DECODER_NAME} from {MODEL_FOLDER})...")

        model = SegmentAnythingONNX(
            encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
            decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
        )
        app_logger.info(f"model instantiated, creating embedding...")
        embedding = model.encode(np_img)
        app_logger.info(f"embedding created, running predict_masks...")
        prediction_masks = model.predict_masks(embedding, prompt)
        app_logger.info(f"predict_masks terminated")
        app_logger.info(f"prediction masks shape:{prediction_masks.shape}, {prediction_masks.dtype}.")

        mask = np.zeros((prediction_masks.shape[2], prediction_masks.shape[3]), dtype=np.uint8)
        for m in prediction_masks[0, :, :, :]:
            mask[m > 0.0] = 255

        mask_unique_values, mask_unique_values_count = serialize(np.unique(mask, return_counts=True))
        app_logger.info(f"mask_unique_values:{mask_unique_values}.")
        app_logger.info(f"mask_unique_values_count:{mask_unique_values_count}.")

        output = {
            "img_size": serialize(img.size),
            "mask_unique_values_count": zip_arrays(mask_unique_values, mask_unique_values_count),
            "masks_dtype": serialize(prediction_masks.dtype),
            "masks_shape": serialize(prediction_masks.shape),
            "matrix": serialize(matrix)
        }
        app_logger.info(f"output:{output}.")
        return output
