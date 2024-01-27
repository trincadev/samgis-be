"""functions useful to convert to/from latitude-longitude coordinates to pixel image coordinates"""
from samgis_core.utilities.type_hints import tuple_float, tuple_float_any

from samgis import app_logger
from samgis.utilities.constants import TILE_SIZE, EARTH_EQUATORIAL_RADIUS
from samgis.utilities.type_hints import ImagePixelCoordinates
from samgis.utilities.type_hints import LatLngDict


def _get_latlng2pixel_projection(latlng: LatLngDict) -> ImagePixelCoordinates:
    from math import log, pi, sin

    app_logger.debug(f"latlng: {type(latlng)}, value:{latlng}.")
    app_logger.debug(f'latlng lat: {type(latlng.lat)}, value:{latlng.lat}.')
    app_logger.debug(f'latlng lng: {type(latlng.lng)}, value:{latlng.lng}.')
    try:
        sin_y: float = sin(latlng.lat * pi / 180)
        app_logger.debug(f"sin_y, #1:{sin_y}.")
        sin_y = min(max(sin_y, -0.9999), 0.9999)
        app_logger.debug(f"sin_y, #2:{sin_y}.")
        x = TILE_SIZE * (0.5 + latlng.lng / 360)
        app_logger.debug(f"x:{x}.")
        y = TILE_SIZE * (0.5 - log((1 + sin_y) / (1 - sin_y)) / (4 * pi))
        app_logger.debug(f"y:{y}.")

        return {"x": x, "y": y}
    except Exception as e_get_latlng2pixel_projection:
        app_logger.error(f'args type:{type(latlng)}, {latlng}.')
        app_logger.exception(f'e_get_latlng2pixel_projection:{e_get_latlng2pixel_projection}.', exc_info=True)
        raise e_get_latlng2pixel_projection


def _get_point_latlng_to_pixel_coordinates(latlng: LatLngDict, zoom: int | float) -> ImagePixelCoordinates:
    from math import floor

    try:
        world_coordinate: ImagePixelCoordinates = _get_latlng2pixel_projection(latlng)
        app_logger.debug(f"world_coordinate:{world_coordinate}.")
        scale: int = pow(2, zoom)
        app_logger.debug(f"scale:{scale}.")
        return ImagePixelCoordinates(
            x=floor(world_coordinate["x"] * scale),
            y=floor(world_coordinate["y"] * scale)
        )
    except Exception as e_format_latlng_to_pixel_coordinates:
        app_logger.error(f'latlng type:{type(latlng)}, {latlng}.')
        app_logger.error(f'zoom type:{type(zoom)}, {zoom}.')
        app_logger.exception(f'e_format_latlng_to_pixel_coordinates:{e_format_latlng_to_pixel_coordinates}.',
                             exc_info=True)
        raise e_format_latlng_to_pixel_coordinates


def get_latlng_to_pixel_coordinates(
        latlng_origin_ne: LatLngDict,
        latlng_origin_sw: LatLngDict,
        latlng_current_point: LatLngDict,
        zoom: int | float,
        k: str
) -> ImagePixelCoordinates:
    """
    Parse the input request lambda event

    Args:
        latlng_origin_ne: NE latitude-longitude origin point
        latlng_origin_sw: SW latitude-longitude origin point
        latlng_current_point: latitude-longitude prompt point
        zoom: Level of detail
        k: prompt type

    Returns:
        ImagePixelCoordinates: pixel image coordinate point
    """
    app_logger.debug(f"latlng_origin - {k}: {type(latlng_origin_ne)}, value:{latlng_origin_ne}.")
    app_logger.debug(f"latlng_current_point - {k}: {type(latlng_current_point)}, value:{latlng_current_point}.")
    latlng_map_origin_ne = _get_point_latlng_to_pixel_coordinates(latlng_origin_ne, zoom)
    latlng_map_origin_sw = _get_point_latlng_to_pixel_coordinates(latlng_origin_sw, zoom)
    latlng_map_current_point = _get_point_latlng_to_pixel_coordinates(latlng_current_point, zoom)
    diff_coord_x = abs(latlng_map_origin_sw["x"] - latlng_map_current_point["x"])
    diff_coord_y = abs(latlng_map_origin_ne["y"] - latlng_map_current_point["y"])
    point = ImagePixelCoordinates(x=diff_coord_x, y=diff_coord_y)
    app_logger.debug(f"point type - {k}: {point}.")
    return point


def _from4326_to3857(lat: float, lon: float) -> tuple_float or tuple_float_any:
    from math import radians, log, tan

    x_tile: float = radians(lon) * EARTH_EQUATORIAL_RADIUS
    y_tile: float = log(tan(radians(45 + lat / 2.0))) * EARTH_EQUATORIAL_RADIUS
    return x_tile, y_tile


def _deg2num(lat: float, lon: float, zoom: int):
    from math import radians, pi, asinh, tan

    n = 2 ** zoom
    x_tile = ((lon + 180) / 360 * n)
    y_tile = (1 - asinh(tan(radians(lat))) / pi) * n / 2
    return x_tile, y_tile
