"""functions useful to convert to/from latitude-longitude coordinates to pixel image coordinates"""
import math

from src import app_logger
from src.utilities.constants import TILE_SIZE
from src.utilities.type_hints import LatLngDict
from src.utilities.type_hints import ImagePixelCoordinates


def _get_latlng2pixel_projection(latlng: LatLngDict) -> ImagePixelCoordinates:
    app_logger.debug(f"latlng: {type(latlng)}, value:{latlng}.")
    app_logger.debug(f'latlng lat: {type(latlng.lat)}, value:{latlng.lat}.')
    app_logger.debug(f'latlng lng: {type(latlng.lng)}, value:{latlng.lng}.')
    try:
        sin_y: float = math.sin(latlng.lat * math.pi / 180)
        app_logger.debug(f"sin_y, #1:{sin_y}.")
        sin_y = min(max(sin_y, -0.9999), 0.9999)
        app_logger.debug(f"sin_y, #2:{sin_y}.")
        x = TILE_SIZE * (0.5 + latlng.lng / 360)
        app_logger.debug(f"x:{x}.")
        y = TILE_SIZE * (0.5 - math.log((1 + sin_y) / (1 - sin_y)) / (4 * math.pi))
        app_logger.debug(f"y:{y}.")

        return {"x": x, "y": y}
    except Exception as e_get_latlng2pixel_projection:
        app_logger.error(f'e_get_latlng2pixel_projection:{e_get_latlng2pixel_projection}.')
        raise e_get_latlng2pixel_projection


def _get_point_latlng_to_pixel_coordinates(latlng: LatLngDict, zoom: int | float) -> ImagePixelCoordinates:
    try:
        world_coordinate: ImagePixelCoordinates = _get_latlng2pixel_projection(latlng)
        app_logger.debug(f"world_coordinate:{world_coordinate}.")
        scale: int = pow(2, zoom)
        app_logger.debug(f"scale:{scale}.")
        return ImagePixelCoordinates(
            x=math.floor(world_coordinate["x"] * scale),
            y=math.floor(world_coordinate["y"] * scale)
        )
    except Exception as e_format_latlng_to_pixel_coordinates:
        app_logger.error(f'format_latlng_to_pixel_coordinates:{e_format_latlng_to_pixel_coordinates}.')
        raise e_format_latlng_to_pixel_coordinates


def get_latlng_to_pixel_coordinates(
        latlng_origin_ne: LatLngDict,
        latlng_origin_sw: LatLngDict,
        latlng_current_point: LatLngDict,
        zoom: int | float,
        k: str
) -> ImagePixelCoordinates:
    """
    Parse the input request lambda event.

    Args:
        latlng_origin_ne: NE latitude-longitude origin point
        latlng_origin_sw: SW latitude-longitude origin point
        latlng_current_point: latitude-longitude prompt point
        zoom: zoom value
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
