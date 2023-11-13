# Press the green button in the gutter to run the script.
import json
from pathlib import Path
from typing import List

import numpy as np
import rasterio
from PIL import Image

from src import app_logger, MODEL_FOLDER
from src.io.tiles_to_tiff import convert
from src.io.tms2geotiff import save_geotiff_gdal
from src.prediction_api.sam_onnx import SegmentAnythingONNX
from src.utilities.constants import MODEL_ENCODER_NAME, ZOOM, MODEL_DECODER_NAME, ROOT
from src.utilities.serialize import serialize


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


def samexporter_predict(bbox, prompt: list[dict], zoom: float = ZOOM, model_name: str = "fastsam") -> dict:
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

        img, matrix = convert(
            bounding_box=bbox,
            zoom=int(zoom)
        )

        pt0, pt1 = bbox
        rio_output = f"/tmp/downloaded_rio_{pt0[0]}_{pt0[1]}_{pt1[0]}_{pt1[1]}.tif"
        save_geotiff_gdal(img, rio_output, matrix)
        app_logger.info(f"saved downloaded geotiff image to {rio_output}...")

        np_img = np.array(img)
        app_logger.info(f"## img type {type(np_img)}, prompt:{prompt}.")

        app_logger.info(f"onnxruntime input shape/size (shape if PIL) {np_img.size},"
                        f"start to initialize SamGeo instance:")
        try:
            app_logger.info(f"onnxruntime input shape (NUMPY) {np_img.shape}.")
        except Exception as e_shape:
            app_logger.error(f"e_shape:{e_shape}.")
        app_logger.info(f"use {model_name} model, ENCODER model {MODEL_ENCODER_NAME} and"
                        f" {MODEL_DECODER_NAME} from {MODEL_FOLDER}): model instantiated, creating embedding...")
        embedding = models_instance.encode(np_img)
        app_logger.info(f"embedding created, running predict_masks...")
        prediction_masks = models_instance.predict_masks(embedding, prompt)
        app_logger.info(f"predict_masks terminated...")
        app_logger.info(f"predict_masks terminated, prediction masks shape:{prediction_masks.shape}, {prediction_masks.dtype}.")
        pt0, pt1 = bbox
        prediction_masks_output = f"/tmp/prediction_masks_{pt0[0]}_{pt0[1]}_{pt1[0]}_{pt1[1]}.npy"
        np.save(
            prediction_masks_output,
            prediction_masks, allow_pickle=True, fix_imports=True
        )
        app_logger.info(f"saved prediction_masks:{prediction_masks_output}.")

        # mask = np.zeros((prediction_masks.shape[2], prediction_masks.shape[3]), dtype=np.uint8)
        # app_logger.info(f"output mask shape:{mask.shape}, {mask.dtype}.")
        # ## todo: convert to geojson directly within the loop to avoid merging two objects
        # for n, m in enumerate(prediction_masks[0, :, :, :]):
        #     app_logger.info(f"## {n} mask => m shape:{mask.shape}, {mask.dtype}.")
        #     mask[m > 0.0] = 255
        prediction_masks0 = prediction_masks[0]
        app_logger.info(f"prediction_masks0 shape:{prediction_masks0.shape}.")

        try:
            pmf = np.sum(prediction_masks0, axis=0).astype(np.uint8)
        except Exception as e_sum_pmf:
            app_logger.error(f"e_sum_pmf:{e_sum_pmf}.")
            pmf = prediction_masks0[0]
        app_logger.info(f"creating pil image from prediction mask with shape {pmf.shape}.")
        pil_pmf = Image.fromarray(pmf)
        pil_pmf_output = f"/tmp/pil_pmf_{pmf.shape[0]}_{pmf.shape[1]}.png"
        pil_pmf.save(pil_pmf_output)
        app_logger.info(f"saved pil_pmf:{pil_pmf_output}.")

        mask = np.zeros(pmf.shape, dtype=np.uint8)
        mask[pmf > 0] = 255

        # cv2.imwrite(f"/tmp/cv2_mask_predicted_{mask.shape[0]}_{mask.shape[1]}_{mask.shape[2]}.png", mask)
        pil_mask = Image.fromarray(mask)
        pil_mask_predicted_output = f"/tmp/pil_mask_predicted_{mask.shape[0]}_{mask.shape[1]}.png"
        pil_mask.save(pil_mask_predicted_output)
        app_logger.info(f"saved pil_mask_predicted:{pil_mask_predicted_output}.")

        mask_unique_values, mask_unique_values_count = serialize(np.unique(mask, return_counts=True))
        app_logger.info(f"mask_unique_values:{mask_unique_values}.")
        app_logger.info(f"mask_unique_values_count:{mask_unique_values_count}.")

        app_logger.info(f"read geotiff:{rio_output}: create shapes_generator...")
        # app_logger.info(f"image/geojson transform:{transform}: create shapes_generator...")
        with rasterio.open(rio_output, "r", driver="GTiff") as rio_src:
            band = rio_src.read()
            try:
                transform = load_affine_transformation_from_matrix(matrix)
                app_logger.info(f"geotiff band:{band.shape}, type: {type(band)}, dtype: {band.dtype}.")
                app_logger.info(f"geotiff band:{mask.shape}.")
                app_logger.info(f"transform from matrix:{transform}.")
                app_logger.info(f"rio_src crs:{rio_src.crs}.")
                app_logger.info(f"rio_src transform:{rio_src.transform}.")
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
            app_logger.info(f"created shapes_generator.")
            shapes_list = list(shapes_generator)
            app_logger.info(f"created {len(shapes_list)} polygons.")
            gpd_polygonized_raster = GeoDataFrame.from_features(shapes_list, crs="EPSG:3857")
            app_logger.info(f"created a GeoDataFrame...")
            geojson = gpd_polygonized_raster.to_json(to_wgs84=True)
            app_logger.info(f"created geojson...")

            output_geojson = str(Path(ROOT) / "geojson_output.json")
            with open(output_geojson, "w") as jj_out:
                app_logger.info(f"writing geojson file to {output_geojson}.")
                json.dump(json.loads(geojson), jj_out)
                app_logger.info(f"geojson file written to {output_geojson}.")

            return {
                "geojson": geojson,
                "n_shapes_geojson": len(shapes_list),
                "n_predictions": len(prediction_masks),
                # "n_pixels_predictions": zip_arrays(mask_unique_values, mask_unique_values_count),
            }
    except ImportError as e:
        app_logger.error(f"Error trying import module:{e}.")
