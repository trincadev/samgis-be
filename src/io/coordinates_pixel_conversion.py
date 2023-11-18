import math
from typing import TypedDict

from src import app_logger
from src.utilities.constants import TILE_SIZE


class PixelCoordinate(TypedDict):
    x: int
    y: int


def get_latlng2pixel_projection(latlng) -> PixelCoordinate:
    app_logger.info(f"latlng: {type(latlng)}, value:{latlng}.")
    app_logger.info(f'latlng lat: {type(latlng["lat"])}, value:{latlng["lat"]}.')
    app_logger.info(f'latlng lng: {type(latlng["lng"])}, value:{latlng["lng"]}.')
    try:
        sin_y: float = math.sin(latlng["lat"] * math.pi / 180)
        app_logger.info(f"sin_y, #1:{sin_y}.")
        sin_y = min(max(sin_y, -0.9999), 0.9999)
        app_logger.info(f"sin_y, #2:{sin_y}.")
        x = TILE_SIZE * (0.5 + latlng["lng"] / 360)
        app_logger.info(f"x:{x}.")
        y = TILE_SIZE * (0.5 - math.log((1 + sin_y) / (1 - sin_y)) / (4 * math.pi))
        app_logger.info(f"y:{y}.")

        return {"x": x, "y": y}
    except Exception as e_get_latlng2pixel_projection:
        app_logger.error(f'e_get_latlng2pixel_projection:{e_get_latlng2pixel_projection}.')
        raise e_get_latlng2pixel_projection


def get_point_latlng_to_pixel_coordinates(latlng, zoom: int) -> PixelCoordinate:
    try:
        world_coordinate: PixelCoordinate = get_latlng2pixel_projection(latlng)
        app_logger.info(f"world_coordinate:{world_coordinate}.")
        scale: int = pow(2, zoom)
        app_logger.info(f"scale:{scale}.")
        return PixelCoordinate(
            x=math.floor(world_coordinate["x"] * scale),
            y=math.floor(world_coordinate["y"] * scale)
        )
    except Exception as e_format_latlng_to_pixel_coordinates:
        app_logger.error(f'format_latlng_to_pixel_coordinates:{e_format_latlng_to_pixel_coordinates}.')
        raise e_format_latlng_to_pixel_coordinates


def get_latlng_to_pixel_coordinates(latlng_origin_ne, latlng_origin_sw, latlng_current_point, zoom, k: str):
    app_logger.info(f"latlng_origin - {k}: {type(latlng_origin_ne)}, value:{latlng_origin_ne}.")
    app_logger.info(f"latlng_current_point - {k}: {type(latlng_current_point)}, value:{latlng_current_point}.")
    latlng_map_origin_ne = get_point_latlng_to_pixel_coordinates(latlng_origin_ne, zoom)
    latlng_map_origin_sw = get_point_latlng_to_pixel_coordinates(latlng_origin_sw, zoom)
    latlng_map_current_point = get_point_latlng_to_pixel_coordinates(latlng_current_point, zoom)
    diff_coord_x = abs(latlng_map_origin_sw["x"] - latlng_map_current_point["x"])
    diff_coord_y = abs(latlng_map_origin_ne["y"] - latlng_map_current_point["y"])
    point = PixelCoordinate(x=diff_coord_x, y=diff_coord_y)
    app_logger.info(f"point type - {k}: {point}.")
    return point


def get_latlng_coords_list(latlng_point, k: str):
    latlng_current_point = latlng_point[k]
    return [latlng_current_point["lat"], latlng_current_point["lng"]]
