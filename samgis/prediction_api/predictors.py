"""functions using machine learning instance model(s)"""
from datetime import datetime
from os import getenv

from samgis import app_logger, MODEL_FOLDER
from samgis.io.geo_helpers import get_vectorized_raster_as_geojson
from samgis.io.raster_helpers import get_raster_terrain_rgb_like, get_rgb_prediction_image, write_raster_png, write_raster_tiff
from samgis.io.tms2geotiff import download_extent
from samgis.io.wrappers_helpers import check_source_type_is_terrain
from samgis.utilities.constants import DEFAULT_URL_TILES, SLOPE_CELLSIZE
from samgis_core.prediction_api.sam_onnx import SegmentAnythingONNX, get_raster_inference_with_embedding_from_dict
from samgis_core.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME, DEFAULT_INPUT_SHAPE
from samgis_core.utilities.type_hints import LlistFloat, DictStrInt, ListDict


models_dict = {"fastsam": {"instance": None}}
embedding_dict = {}
msg_write_tmp_on_disk = "found option to write images and geojson output..."


def samexporter_predict(
        bbox: LlistFloat,
        prompt: ListDict,
        zoom: float,
        model_name: str = "fastsam",
        source: str = DEFAULT_URL_TILES,
        source_name: str = None
) -> DictStrInt:
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
        source: xyz tile provider object
        source_name: name of tile provider

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
    if check_source_type_is_terrain(source):
        app_logger.info("terrain-rgb like raster: transforms it into a DEM")
        dem = get_raster_terrain_rgb_like(img, source.name)
        # set a slope cell size proportional to the image width
        slope_cellsize = int(img.shape[1] * SLOPE_CELLSIZE / DEFAULT_INPUT_SHAPE[1])
        app_logger.info(f"terrain-rgb like raster: compute slope, curvature using {slope_cellsize} as cell size.")
        img = get_rgb_prediction_image(dem, slope_cellsize)

    folder_write_tmp_on_disk = getenv("WRITE_TMP_ON_DISK", "")
    app_logger.info(f"folder_write_tmp_on_disk:{folder_write_tmp_on_disk}.")
    prefix = f"w{pt1[1]},s{pt1[0]},e{pt0[1]},n{pt0[0]}_"
    if bool(folder_write_tmp_on_disk):
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        app_logger.info(msg_write_tmp_on_disk + f"with coords {prefix}, shape:{img.shape}, {len(img.shape)}.")
        if img.shape and len(img.shape) == 2:
            write_raster_tiff(img, transform, f"{source_name}_{prefix}_{now}_", f"raw_tiff", folder_write_tmp_on_disk)
        if img.shape and len(img.shape) == 3 and img.shape[2] == 3:
            write_raster_png(img, transform, f"{source_name}_{prefix}_{now}_", f"raw_img", folder_write_tmp_on_disk)

    app_logger.info(
        f"img type {type(img)} with shape/size:{img.size}, transform type: {type(transform)}, transform:{transform}.")
    app_logger.info(f"source_name:{source_name}, source_name type:{type(source_name)}.")
    embedding_key = f"{source_name}_z{zoom}_w{pt1[1]},s{pt1[0]},e{pt0[1]},n{pt0[0]}"
    mask, n_predictions = get_raster_inference_with_embedding_from_dict(
        img, prompt, models_instance, model_name, embedding_key, embedding_dict)
    app_logger.info(f"created {n_predictions} masks, type {type(mask)}, size {mask.size}: preparing geojson conversion")
    app_logger.info(f"mask shape:{mask.shape}.")
    return {
        "n_predictions": n_predictions,
        **get_vectorized_raster_as_geojson(mask, transform)
    }
