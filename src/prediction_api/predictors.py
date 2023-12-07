"""functions using machine learning instance model(s)"""
from numpy import array as np_array, uint8, zeros, ndarray

from src import app_logger, MODEL_FOLDER
from src.io.geo_helpers import get_vectorized_raster_as_geojson
from src.io.tms2geotiff import download_extent
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME, DEFAULT_TMS
from src.utilities.type_hints import llist_float, dict_str_int, list_dict, tuple_ndarr_int, PIL_Image

models_dict = {"fastsam": {"instance": None}}


def samexporter_predict(
        bbox: llist_float,
        prompt: list_dict,
        zoom: float,
        model_name: str = "fastsam",
        source: str = DEFAULT_TMS
) -> dict_str_int:
    """
    Return predictions as a geojson from a geo-referenced image using the given input prompt.

    1. if necessary instantiate a segment anything machine learning instance model
    2. download a geo-referenced raster image delimited by the coordinates bounding box (bbox)
    3. get a prediction image from the segment anything instance model using the input prompt
    4. get a geo-referenced geojson from the prediction image

    Args:
        bbox: coordinates bounding box
        prompt: machine learning input prompt
        zoom: Level of detail
        model_name: machine learning model name
        source: xyz

    Returns:
        Affine transform
    """
    if models_dict[model_name]["instance"] is None:
        app_logger.info(f"missing instance model {model_name}, instantiating it now!")
        model_instance = SegmentAnythingONNX(
            encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
            decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
        )
        models_dict[model_name]["instance"] = model_instance
    app_logger.debug(f"using a {model_name} instance model...")
    models_instance = models_dict[model_name]["instance"]

    pt0, pt1 = bbox
    app_logger.info(f"tile_source: {source}: downloading geo-referenced raster with bbox {bbox}, zoom {zoom}.")
    img, transform = download_extent(w=pt1[1], s=pt1[0], e=pt0[1], n=pt0[0], zoom=zoom, source=source)
    app_logger.info(
        f"img type {type(img)} with shape/size:{img.size}, transform type: {type(transform)}, transform:{transform}.")

    mask, n_predictions = get_raster_inference(img, prompt, models_instance, model_name)
    app_logger.info(f"created {n_predictions} masks, preparing conversion to geojson...")
    return {
        "n_predictions": n_predictions,
        **get_vectorized_raster_as_geojson(mask, transform)
    }


def get_raster_inference(
        img: PIL_Image or ndarray, prompt: list_dict, models_instance: SegmentAnythingONNX, model_name: str
     ) -> tuple_ndarr_int:
    """
    Wrapper for rasterio Affine from_gdal method

    Args:
        img: input PIL Image
        prompt: list of prompt dict
        models_instance: SegmentAnythingONNX instance model
        model_name: model name string

    Returns:
        raster prediction mask, prediction number
    """
    np_img = np_array(img)
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
    len_inference_out = len(inference_out[0, :, :, :])
    app_logger.info(f"Created {len_inference_out} prediction_masks,"
                    f"shape:{inference_out.shape}, dtype:{inference_out.dtype}.")
    mask = zeros((inference_out.shape[2], inference_out.shape[3]), dtype=uint8)
    for n, m in enumerate(inference_out[0, :, :, :]):
        app_logger.debug(f"{n}th of prediction_masks shape {inference_out.shape}"
                         f" => mask shape:{mask.shape}, {mask.dtype}.")
        mask[m > 0.0] = 255
    return mask, len_inference_out
