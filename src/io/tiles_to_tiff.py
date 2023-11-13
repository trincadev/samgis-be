"""Async download raster tiles"""
import os
from pathlib import Path

import numpy as np

from src import app_logger, PROJECT_ROOT_FOLDER
from src.io.helpers import get_lat_lon_coords, merge_tiles, get_geojson_square_angles, crop_raster
from src.io.tms2geotiff import download_extent, save_geotiff_gdal
from src.utilities.constants import COMPLETE_URL_TILES, DEFAULT_TMS
from src.utilities.type_hints import ts_llist2

COOKIE_SESSION = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
}


def load_affine_transformation_from_matrix(matrix_source_coeffs):
    from affine import Affine

    if len(matrix_source_coeffs) != 6:
        raise ValueError(f"Expected 6 coefficients, found {len(matrix_source_coeffs)};"
                         f"argument type: {type(matrix_source_coeffs)}.")

    try:
        a, d, b, e, c, f = (float(x) for x in matrix_source_coeffs)
        center = tuple.__new__(Affine, [a, b, c, d, e, f, 0.0, 0.0, 1.0])
        return center * Affine.translation(-0.5, -0.5)
    except Exception as e:
        app_logger.error(f"exception:{e}, check https://github.com/rasterio/affine project for updates")


# @timing_decorator
def convert(bounding_box: ts_llist2, zoom: int) -> tuple:
    """
    Starting from a bounding box of two couples of latitude and longitude coordinate values, recognize a stratovolcano from an RGB image. The algorithm
    create the image composing three channels as slope, DEM (Digital Elevation Model) and curvature. In more detail:

    - download a series of terrain DEM (Digital Elevation Model) raster tiles enclosed within that bounding box
    - merge all the downloaded rasters
    - crop the merged raster
    - process the cropped raster to extract slope and curvature (1st and 2nd degree derivative)
    - produce three raster channels (DEM, slope and curvature rasters) to produce an RGB raster image
    - submit the RGB image to a remote machine learning service to try to recognize a polygon representing a stratovolcano
    - the output of the machine learning service is a json, so we need to georeferencing it
    - finally we return a dict as response containing
    - uploaded_file_name
    - bucket_name
    - prediction georeferenced geojson-like dict

    Args:
        bounding_box: float latitude/longitude bounding box
        zoom: integer zoom value

    Returns:
        dict: uploaded_file_name (str), bucket_name (str), prediction_georef (dict), n_total_obj_prediction (str)

    """
    import tempfile

    # from src.surferdtm_prediction_api.utilities.constants import NODATA_VALUES
    # from src.surferdtm_prediction_api.utilities.utilities import setup_logging
    # from src.surferdtm_prediction_api.raster.elaborate_images import elaborate_images.get_rgb_prediction_image
    # from src.surferdtm_prediction_api.raster.prediction import model_prediction
    # from src.surferdtm_prediction_api.geo.helpers import get_lat_lon_coords, merge_tiles, crop_raster, get_prediction_georeferenced, \
    #     get_geojson_square_angles, get_perc

    # app_logger = setup_logging(debug)
    ext = "tif"
    debug = False
    tile_source = COMPLETE_URL_TILES
    app_logger.info(f"start_args: tile_source:{tile_source},bounding_box:{bounding_box},zoom:{zoom}.")

    try:
        import rasterio

        lon_min, lat_min, lon_max, lat_max = get_lat_lon_coords(bounding_box)

        with tempfile.TemporaryDirectory() as input_tmp_dir:
            # with tempfile.TemporaryDirectory() as output_tmp_dir:
            output_tmp_dir = input_tmp_dir
            app_logger.info(f'tile_source: {tile_source}!')
            app_logger.info(f'created temporary input/output directory: {input_tmp_dir} => {output_tmp_dir}!')
            pt0, pt1 = bounding_box
            app_logger.info("downloading...")
            img, matrix = download_extent(DEFAULT_TMS, pt0[0], pt0[1], pt1[0], pt1[1], zoom)

            app_logger.info(f'img: type {type(img)}, len_matrix:{len(matrix)}, matrix {matrix}.')
            app_logger.info(f'img: size (shape if PIL) {img.size}.')
            try:
                np_img = np.array(img)
                app_logger.info(f'img: shape (numpy) {np_img.shape}.')
            except Exception as e_shape:
                app_logger.info(f'e_shape {e_shape}.')
                raise e_shape
            img.save(f"/tmp/downloaded_{pt0[0]}_{pt0[1]}_{pt1[0]}_{pt1[1]}.png")
            app_logger.info("saved PIL image")

            return img, matrix
            # app_logger.info("prepare writing...")
            # app_logger.info(f'img: type {type(img)}, len_matrix:{len(matrix)}, matrix {matrix}.')
            #
            # rio_output = str(Path(output_tmp_dir) / "downloaded_rio.tif")
            # app_logger.info(f'writing to disk img, output file {rio_output}.')
            # save_geotiff_gdal(img, rio_output, matrix)
            # app_logger.info(f'img written to output file {rio_output}.')
            #
            # source_tiles = os.path.join(input_tmp_dir, f"*.{ext}")
            # suffix_raster_filename = f"{lon_min},{lat_min},{lon_max},{lat_max}_{zoom}"
            # merged_raster_filename = f"merged_{suffix_raster_filename}.{ext}"
            # masked_raster_filename = f"masked_{suffix_raster_filename}.{ext}"
            # output_merged_path = os.path.join(output_tmp_dir, merged_raster_filename)
            #
            # app_logger.info(f"try merging tiles to:{output_merged_path}.")
            # merge_tiles(source_tiles, output_merged_path, input_tmp_dir)
            # app_logger.info(f"Merge complete, try crop...")
            # geojson = get_geojson_square_angles(bounding_box, name=suffix_raster_filename, debug=debug)
            # app_logger.info(f"geojson to convert:{geojson}.")
            #
            # crop_raster_output = crop_raster(output_merged_path, geojson, debug=False)
            # masked_raster = crop_raster_output["masked_raster"]
            # masked_meta = crop_raster_output["masked_meta"]
            # masked_transform = crop_raster_output["masked_transform"]
            #
            # return masked_raster, masked_transform

            # app_logger.info(f"resampling -32768 values as NaN for file:{masked_raster_filename}.")
            # masked_raster = masked_raster[0].astype(float)
            # masked_raster[masked_raster == NODATA_VALUES] = 0
            # # info
            # nan_count = np.count_nonzero(~np.isnan(masked_raster))
            # total_count = masked_raster.shape[-1] * masked_raster.shape[-2]
            # perc = get_perc(nan_count, total_count)
            # msg = f"img:{masked_raster_filename}, shape:{masked_raster.shape}: found {nan_count} not-NaN values / {total_count} total, %:{perc}."
            # app_logger.info(msg)
            #
            # app_logger.info(f"crop complete, shape:{masked_raster.shape}, dtype:{masked_raster.dtype}. Create RGB image...")
            # # rgb_filename, rgb_path = elaborate_images.get_rgb_prediction_image(masked_raster, slope_cellsize, suffix_raster_filename, output_tmp_dir, debug=debug)
            # # prediction = model_prediction(rgb_path, project_name=model_project_name, version=model_version, api_key=model_api_key, debug=False)
            #
            # mask_vectorizing = np.ones(masked_raster.shape).astype(rasterio.uint8)
            # app_logger.info(f"prediction success, try to geo-referencing it with transform:{masked_transform}.")
            #
            # app_logger.info(
            #     f"image/geojson origin matrix:, masked_transform:{masked_transform}: create shapes_generator...")
            # app_logger.info(f"raster mask to vectorize, type:{type(mask_vectorizing)}.")
            # app_logger.info(f"raster mask to vectorize: shape:{mask_vectorizing.shape}, {mask_vectorizing.dtype}.")
            #
            # shapes_generator = ({
            #     'properties': {'raster_val': v}, 'geometry': s}
            #     for i, (s, v)
            #     in enumerate(shapes(mask_vectorizing, mask=mask_vectorizing, transform=masked_transform))
            # )
            # shapes_list = list(shapes_generator)
            # app_logger.info(f"created {len(shapes_list)} polygons.")
            # gpd_polygonized_raster = GeoDataFrame.from_features(shapes_list, crs="EPSG:3857")
            # app_logger.info(f"created a GeoDataFrame: type {type(gpd_polygonized_raster)}.")
            # geojson = gpd_polygonized_raster.to_json(to_wgs84=True)
            # app_logger.info(f"created geojson: type {type(geojson)}, len:{len(geojson)}.")
            # serialized_geojson = serialize.serialize(geojson)
            # app_logger.info(f"created serialized_geojson: type {type(serialized_geojson)}, len:{len(serialized_geojson)}.")
            # loaded_geojson = json.loads(geojson)
            # app_logger.info(f"loaded_geojson: type {type(loaded_geojson)}, loaded_geojson:{loaded_geojson}.")
            # n_feats = len(loaded_geojson["features"])
            # app_logger.info(f"created geojson: n_feats {n_feats}.")
            #
            # output_geojson = str(Path(ROOT) / "geojson_output.json")
            # with open(output_geojson, "w") as jj_out:
            #     app_logger.info(f"writing geojson file to {output_geojson}.")
            #     json.dump(loaded_geojson, jj_out)
            #     app_logger.info(f"geojson file written to {output_geojson}.")
            #
            # # prediction_georef = helpers.get_prediction_georeferenced(prediction, masked_transform, skip_conditions_list, debug=debug)
            # app_logger.info(f"success on geo-referencing prediction.")
            # # app_logger.info(f"success on creating file {rgb_filename}, now try upload it to bucket_name {bucket_name}...")
            # return {
            #     # "uploaded_file_name": rgb_filename,
            #     "geojson": loaded_geojson,
            #     # "prediction_georef": prediction_georef,
            #     "n_total_obj_prediction": n_feats
            # }
    except ImportError as e_import_convert:
        app_logger.error(f"e0:{e_import_convert}.")
        raise e_import_convert


if __name__ == '__main__':
    from PIL import Image

    npy_file = "prediction_masks_46.27697017893455_9.616470336914064_46.11441972281433_9.264907836914064.npy"
    prediction_masks = np.load(Path(PROJECT_ROOT_FOLDER) / "tmp" / "try_by_steps" / "t0" / npy_file)

    print("#")
