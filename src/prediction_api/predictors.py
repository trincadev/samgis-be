# Press the green button in the gutter to run the script.
import tempfile
from pathlib import Path
from typing import List

import numpy as np
import rasterio

from src import app_logger, MODEL_FOLDER
from src.io.tiles_to_tiff import convert
from src.io.tms2geotiff import save_geotiff_gdal
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, MODEL_DECODER_NAME


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


def samexporter_predict(bbox, prompt: list[dict], zoom: float, model_name: str = "fastsam") -> dict:
    try:
        from rasterio.features import shapes
        from geopandas import GeoDataFrame

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
            img, matrix = convert(
                bounding_box=bbox,
                zoom=int(zoom)
            )
            app_logger.debug(f"## img type {type(img)} with shape/size:{img.size}, matrix:{matrix}.")

            pt0, pt1 = bbox
            rio_output = str(Path(input_tmp_dir) / f"downloaded_rio_{pt0[0]}_{pt0[1]}_{pt1[0]}_{pt1[1]}.tif")
            app_logger.debug(f"saving downloaded geotiff image to {rio_output}...")
            save_geotiff_gdal(img, rio_output, matrix)
            app_logger.info(f"saved downloaded geotiff image to {rio_output}...")

            np_img = np.array(img)
            app_logger.info(f"## img type {type(np_img)}, prompt:{prompt}.")

            app_logger.info(f"onnxruntime input shape/size (shape if PIL) {np_img.size}.")
            try:
                app_logger.info(f"onnxruntime input shape (NUMPY) {np_img.shape}.")
            except Exception as e_shape:
                app_logger.error(f"e_shape:{e_shape}.")
            app_logger.info(f"instantiated model {model_name}, ENCODER {MODEL_ENCODER_NAME}, "
                            f"DECODER {MODEL_DECODER_NAME} from {MODEL_FOLDER}: Creating embedding...")
            embedding = models_instance.encode(np_img)
            app_logger.info(f"embedding created, running predict_masks with prompt {prompt}...")
            prediction_masks = models_instance.predict_masks(embedding, prompt)
            app_logger.info(f"Created {len(prediction_masks)} prediction_masks,"
                            f"shape:{prediction_masks.shape}, dtype:{prediction_masks.dtype}.")

            mask = np.zeros((prediction_masks.shape[2], prediction_masks.shape[3]), dtype=np.uint8)
            for n, m in enumerate(prediction_masks[0, :, :, :]):
                app_logger.debug(f"## {n} mask => m shape:{mask.shape}, {mask.dtype}.")
                mask[m > 0.0] = 255

            app_logger.info(f"read downloaded geotiff:{rio_output} to create the shapes_generator...")

            with rasterio.open(rio_output, "r", driver="GTiff") as rio_src:
                band = rio_src.read()
                try:
                    app_logger.debug(f"geotiff band:{band.shape}, type: {type(band)}, dtype: {band.dtype}.")
                    app_logger.debug(f"rio_src crs:{rio_src.crs}.")
                    app_logger.debug(f"rio_src transform:{rio_src.transform}.")
                except Exception as e_shape_band:
                    app_logger.error(f"e_shape_band:{e_shape_band}.")
                    raise e_shape_band
                # mask_band = band != 0
                shapes_generator = ({
                    'properties': {'raster_val': v}, 'geometry': s}
                    for i, (s, v)
                    # in enumerate(shapes(mask, mask=(band != 0), transform=rio_src.transform))
                    # use mask=None to avoid using source
                    in enumerate(shapes(mask, mask=None, transform=rio_src.transform))
                )
                app_logger.info(f"created shapes_generator, transform it to a polygon list...")
                shapes_list = list(shapes_generator)
                app_logger.info(f"created {len(shapes_list)} polygons.")
                gpd_polygonized_raster = GeoDataFrame.from_features(shapes_list, crs="EPSG:3857")
                app_logger.info(f"created a GeoDataFrame, export to geojson...")
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
