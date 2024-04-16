"""handle geo-referenced raster images"""
from affine import Affine
from numpy import ndarray as np_ndarray

from samgis_core.utilities.type_hints import ListFloat, DictStrInt, TupleFloat
from samgis import app_logger


def load_affine_transformation_from_matrix(matrix_source_coefficients: ListFloat) -> Affine:
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
        app_logger.exception(f"exception:{e}, check updates on https://github.com/rasterio/affine",
                             extra=e,
                             stack_info=True, exc_info=True)
        raise e


def get_affine_transform_from_gdal(matrix_source_coefficients: ListFloat or TupleFloat) -> Affine:
    """wrapper for rasterio Affine from_gdal method

    Args:
        matrix_source_coefficients: 6 floats ordered by GDAL.

    Returns:
        Affine transform
    """
    return Affine.from_gdal(*matrix_source_coefficients)


def get_vectorized_raster_as_geojson(mask: np_ndarray, transform: TupleFloat) -> DictStrInt:
    """
        Get shapes and values of connected regions in a dataset or array

        Args:
            mask: numpy mask
            transform: tuple of float to transform into an Affine transform

        Returns:
            dict containing the output geojson and the predictions number
    """
    try:
        from rasterio.features import shapes
        from geopandas import GeoDataFrame

        app_logger.debug(f"matrix to consume with rasterio.shapes: {type(transform)}, {transform}.")

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
        try:
            app_logger.error(f"mask type:{type(mask)}.")
            app_logger.error(f"transform type:{type(transform)}, {transform}.")
            app_logger.error(f"mask shape:{mask.shape}, dtype:{mask.dtype}.")
        except Exception as e_shape_dtype:
            app_logger.exception(f"mask shape or dtype not found:{e_shape_dtype}.", exc_info=True)
        app_logger.exception(f"e_shape_band:{e_shape_band}.", exc_info=True)
        raise e_shape_band
