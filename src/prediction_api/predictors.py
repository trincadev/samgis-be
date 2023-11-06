# Press the green button in the gutter to run the script.
import numpy as np
from typing import List

from src import app_logger, MODEL_FOLDER
from src.io.tms2geotiff import download_extent
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, ZOOM, DEFAULT_TMS, MODEL_DECODER_NAME
from src.utilities.serialize import serialize
from src.utilities.type_hints import input_float_tuples


models_dict = {"fastsam": {"instance": None}}


def zip_arrays(arr1, arr2):
    try:
        arr1_list = arr1.tolist()
        arr2_list = arr2.tolist()
        # return {serialize(k): serialize(v) for k, v in zip(arr1_list, arr2_list)}
        d = {}
        for n1, n2 in zip(arr1_list, arr2_list):
            app_logger.info(f"n1:{n1}, type {type(n1)}, n2:{n2}, type {type(n2)}.")
            n1f = str(n1)
            n2f = str(n2)
            app_logger.info(f"n1:{n1}=>{n1f}, n2:{n2}=>{n2f}.")
            d[n1f] = n2f
        app_logger.info(f"zipped dict:{d}.")
        return d
    except Exception as e_zip_arrays:
        app_logger.info(f"exception zip_arrays:{e_zip_arrays}.")
        return {}


def load_affine_transformation_from_matrix(matrix_source_coeffs: List):
    from affine import Affine

    if len(matrix_source_coeffs) != 6:
        raise ValueError(f"Expected 6 coefficients, found {len(matrix_source_coeffs)}; argument type: {type(matrix_source_coeffs)}.")

    try:
        a, d, b, e, c, f = (float(x) for x in matrix_source_coeffs)
        center = tuple.__new__(Affine, [a, b, c, d, e, f, 0.0, 0.0, 1.0])
        return center * Affine.translation(-0.5, -0.5)
    except Exception as e:
        app_logger.error(f"exception:{e}, check https://github.com/rasterio/affine project for updates")


def samexporter_predict(bbox: input_float_tuples, prompt: list[dict], zoom: float = ZOOM, model_name: str = "fastsam") -> dict:
    try:
        from rasterio.features import shapes
        from geopandas import GeoDataFrame

        if models_dict[model_name]["instance"] is None:
            app_logger.info(f"missing instance model {model_name}, instantiating it now")
            model_instance = SegmentAnythingONNX(
                encoder_model_path=MODEL_FOLDER / MODEL_ENCODER_NAME,
                decoder_model_path=MODEL_FOLDER / MODEL_DECODER_NAME
            )
            models_dict[model_name]["instance"] = model_instance
        app_logger.info(f"using a {model_name} instance model...")
        models_instance = models_dict[model_name]["instance"]

        for coord in bbox:
            app_logger.debug(f"bbox coord:{coord}, type:{type(coord)}.")
        app_logger.info(f"start download_extent using bbox:{bbox}, type:{type(bbox)}, download image...")

        pt0 = bbox[0]
        pt1 = bbox[1]
        img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)

        app_logger.info(f"img type {type(img)}, matrix type {type(matrix)}.")
        app_logger.debug(f"matrix values: {serialize(matrix)}.")
        np_img = np.array(img)
        app_logger.debug(f"np_img type {type(np_img)}.")
        app_logger.debug(f"np_img dtype {np_img.dtype}, shape {np_img.shape}.")
        app_logger.info(f"geotiff created with size/shape {img.size} and transform matrix {str(matrix)}, start to initialize SamGeo instance:")
        app_logger.info(f"use {model_name} model, ENCODER model {MODEL_ENCODER_NAME} and {MODEL_DECODER_NAME} from {MODEL_FOLDER}): model instantiated, creating embedding...")
        embedding = models_instance.encode(np_img)
        app_logger.info(f"embedding created, running predict_masks...")
        prediction_masks = models_instance.predict_masks(embedding, prompt)
        app_logger.debug(f"predict_masks terminated...")
        app_logger.info(f"predict_masks terminated, prediction masks shape:{prediction_masks.shape}, {prediction_masks.dtype}.")

        mask = np.zeros((prediction_masks.shape[2], prediction_masks.shape[3]), dtype=np.uint8)
        for m in prediction_masks[0, :, :, :]:
            mask[m > 0.0] = 255

        mask_unique_values, mask_unique_values_count = serialize(np.unique(mask, return_counts=True))
        app_logger.debug(f"mask_unique_values:{mask_unique_values}.")
        app_logger.debug(f"mask_unique_values_count:{mask_unique_values_count}.")

        transform = load_affine_transformation_from_matrix(matrix)
        app_logger.info(f"image/geojson origin matrix:{matrix}, transform:{transform}: create shapes_generator...")
        shapes_generator = ({
            'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v)
            in enumerate(shapes(mask, mask=mask, transform=transform))
        )
        shapes_list = list(shapes_generator)
        app_logger.info(f"created {len(shapes_list)} polygons.")
        gpd_polygonized_raster = GeoDataFrame.from_features(shapes_list, crs="EPSG:3857")
        app_logger.info(f"created a GeoDataFrame...")
        geojson = gpd_polygonized_raster.to_json(to_wgs84=True)
        app_logger.info(f"created geojson...")

        return {
            "geojson": geojson,
            "n_shapes_geojson": len(shapes_list),
            "n_predictions": len(prediction_masks),
            # "n_pixels_predictions": zip_arrays(mask_unique_values, mask_unique_values_count),
        }
    except ImportError as e:
        app_logger.error(f"Error trying import module:{e}.")
