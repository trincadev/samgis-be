"""Async download raster tiles"""
from pathlib import Path

import numpy as np

from src import app_logger, PROJECT_ROOT_FOLDER
from src.io.tms2geotiff import download_extent
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

    tile_source = COMPLETE_URL_TILES
    app_logger.info(f"start_args: tile_source:{tile_source},bounding_box:{bounding_box},zoom:{zoom}.")

    try:
        import rasterio

        app_logger.info(f'tile_source: {tile_source}!')
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

        return img, matrix
    except ImportError as e_import_convert:
        app_logger.error(f"e0:{e_import_convert}.")
        raise e_import_convert


if __name__ == '__main__':
    npy_file = "prediction_masks_46.27697017893455_9.616470336914064_46.11441972281433_9.264907836914064.npy"
    prediction_masks = np.load(Path(PROJECT_ROOT_FOLDER) / "tmp" / "try_by_steps" / "t0" / npy_file)

    print("#")
