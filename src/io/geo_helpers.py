"""handle geo-referenced raster images"""
from affine import Affine
from numpy import ndarray as np_ndarray

from src import app_logger
from src.utilities.type_hints import list_float, tuple_float, dict_str_int


def load_affine_transformation_from_matrix(matrix_source_coefficients: list_float) -> Affine:
    """
    Wrapper for rasterio.Affine.from_gdal() method

    Args:
        matrix_source_coefficients: 6 floats ordered by GDAL.

    Returns:
        Affine transform
    """

    if len(matrix_source_coefficients) != 6:
        raise ValueError(f"Expected 6 coefficients, found {len(matrix_source_coefficients)}; "
                         f"argument type: {type(matrix_source_coefficients)}.")

    try:
        a, d, b, e, c, f = (float(x) for x in matrix_source_coefficients)
        center = tuple.__new__(Affine, [a, b, c, d, e, f, 0.0, 0.0, 1.0])
        return center * Affine.translation(-0.5, -0.5)
    except Exception as e:
        app_logger.error(f"exception:{e}, check https://github.com/rasterio/affine project for updates")
        raise e


def get_affine_transform_from_gdal(matrix_source_coefficients: list_float or tuple_float) -> Affine:
    """wrapper for rasterio Affine from_gdal method

    Args:
        matrix_source_coefficients: 6 floats ordered by GDAL.

    Returns:
        Affine transform
    """
    return Affine.from_gdal(*matrix_source_coefficients)


def get_vectorized_raster_as_geojson(mask: np_ndarray, matrix: tuple_float) -> dict_str_int:
    """
        Get shapes and values of connected regions in a dataset or array

        Args:
            mask: numpy mask
            matrix: tuple of float to transform into an Affine transform

        Returns:
            dict containing the output geojson and the predictions number
    """
    try:
        from rasterio.features import shapes
        from geopandas import GeoDataFrame

        transform = get_affine_transform_from_gdal(matrix)
        app_logger.info(f"transform to consume with rasterio.shapes: {type(transform)}, {transform}.")

        # old value for mask => band != 0
        shapes_generator = ({
            'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v)
            # instead of `enumerate(shapes(mask, mask=(band != 0), transform=rio_src.transform))`
            # use mask=None to avoid using source
            in enumerate(shapes(mask, mask=None, transform=transform))
        )
        app_logger.info("created shapes_generator, transform it to a polygon list...")
        shapes_list = list(shapes_generator)
        app_logger.info(f"created {len(shapes_list)} polygons.")
        gpd_polygonized_raster = GeoDataFrame.from_features(shapes_list, crs="EPSG:3857")
        app_logger.info("created a GeoDataFrame, export to geojson...")
        geojson = gpd_polygonized_raster.to_json(to_wgs84=True)
        app_logger.info("created geojson, preparing API response...")
        return {
            "geojson": geojson,
            "n_shapes_geojson": len(shapes_list)
        }
    except Exception as e_shape_band:
        app_logger.error(f"e_shape_band:{e_shape_band}.")
        raise e_shape_band
