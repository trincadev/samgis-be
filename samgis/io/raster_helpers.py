"""helpers for computer vision duties"""
import numpy as np
from numpy import ndarray

from samgis import app_logger
from samgis.utilities.type_hints import TmsTerrainProvidersNames


def get_nextzen_terrain_rgb_formula(red: ndarray, green: ndarray, blue: ndarray) -> ndarray:
    """
    Compute a 32-bits 2d digital elevation model from a nextzen 'terrarium' (terrain-rgb) raster.
    'Terrarium' format PNG tiles contain raw elevation data in meters, in Mercator projection (EPSG:3857).
    All values are positive with a 32,768 offset, split into the red, green, and blue channels,
    with 16 bits of integer and 8 bits of fraction. To decode:

        (red * 256 + green + blue / 256) - 32768

    More details on https://www.mapzen.com/blog/elevation/

    Args:
        red: red-valued channel image array
        green: green-valued channel image array
        blue: blue-valued channel image array

    Returns:
        ndarray: nextzen 'terrarium' 2d digital elevation model raster at 32 bits

    """
    return (red * 256 + green + blue / 256) - 32768


def get_mapbox__terrain_rgb_formula(red: ndarray, green: ndarray, blue: ndarray) -> ndarray:
    return ((red * 256 * 256 + green * 256 + blue) * 0.1) - 10000


providers_terrain_rgb_formulas = {
    TmsTerrainProvidersNames.MAPBOX_TERRAIN_TILES_NAME: get_mapbox__terrain_rgb_formula,
    TmsTerrainProvidersNames.NEXTZEN_TERRAIN_TILES_NAME: get_nextzen_terrain_rgb_formula
}


def _get_2d_array_from_3d(arr: ndarray) -> ndarray:
    return arr.reshape(arr.shape[0], arr.shape[1])


def _channel_split(arr: ndarray) -> list[ndarray]:
    from numpy import dsplit

    return dsplit(arr, arr.shape[-1])


def get_raster_terrain_rgb_like(arr: ndarray, xyz_provider_name, nan_value_int: int = -12000):
    """
    Compute a 32-bits 2d digital elevation model from a terrain-rgb raster.

    Args:
        arr: rgb raster
        xyz_provider_name: xyz provider
        nan_value_int: threshold int value to replace NaN

    Returns:
        ndarray: 2d digital elevation model raster at 32 bits
    """
    red, green, blue = _channel_split(arr)
    dem_rgb = providers_terrain_rgb_formulas[xyz_provider_name](red, green, blue)
    output = _get_2d_array_from_3d(dem_rgb)
    output[output < nan_value_int] = np.NaN
    return output


def get_rgb_prediction_image(raster_cropped: ndarray, slope_cellsize: int, invert_image: bool = True) -> ndarray:
    """
    Return an RGB image from input numpy array
    
    Args:
        raster_cropped: input numpy array
        slope_cellsize: window size to calculate slope and curvature (1st and 2nd degree array derivative)
        invert_image: 

    Returns:
        tuple of str: image filename, image path (with filename)
    """
    from samgis.utilities.constants import CHANNEL_EXAGGERATIONS_LIST

    try:
        slope, curvature = get_slope_curvature(raster_cropped, slope_cellsize=slope_cellsize)
        channel0 = raster_cropped
        channel1 = normalize_array_list(
            [raster_cropped, slope, curvature], CHANNEL_EXAGGERATIONS_LIST, title=f"channel1_normlist")
        channel2 = curvature

        return get_rgb_image(channel0, channel1, channel2, invert_image=invert_image)
    except ValueError as ve_get_rgb_prediction_image:
        msg = f"ve_get_rgb_prediction_image:{ve_get_rgb_prediction_image}."
        app_logger.error(msg)
        raise ve_get_rgb_prediction_image


def get_rgb_image(arr_channel0: ndarray, arr_channel1: ndarray, arr_channel2: ndarray,
                  invert_image: bool = True) -> ndarray:
    """
    Return an RGB image from input R,G,B channel arrays

    Args:
        arr_channel0: channel image 0
        arr_channel1: channel image 1
        arr_channel2: channel image 2
        invert_image: invert the RGB image channel order

    Returns:
        ndarray: RGB image

    """
    try:
        # RED curvature, GREEN slope, BLUE dem, invert_image=True
        if len(arr_channel0.shape) != 2:
            msg = f"arr_size, wrong type:{type(arr_channel0)} or arr_size:{arr_channel0.shape}."
            app_logger.error(msg)
            raise ValueError(msg)
        data_rgb = np.zeros((arr_channel0.shape[0], arr_channel0.shape[1], 3), dtype=np.uint8)
        app_logger.debug(f"arr_container data_rgb, type:{type(data_rgb)}, arr_shape:{data_rgb.shape}.")
        data_rgb[:, :, 0] = normalize_array(
            arr_channel0.astype(float), high=1, norm_type="float", title=f"RGB:channel0") * 64
        data_rgb[:, :, 1] = normalize_array(
            arr_channel1.astype(float), high=1, norm_type="float", title=f"RGB:channel1") * 128
        data_rgb[:, :, 2] = normalize_array(
            arr_channel2.astype(float), high=1, norm_type="float", title=f"RGB:channel2") * 192
        if invert_image:
            data_rgb = np.bitwise_not(data_rgb)
        return data_rgb
    except ValueError as ve_get_rgb_image:
        msg = f"ve_get_rgb_image:{ve_get_rgb_image}."
        app_logger.error(msg)
        raise ve_get_rgb_image


def get_slope_curvature(dem: ndarray, slope_cellsize: int, title: str = "") -> tuple[ndarray, ndarray]:
    """
    Return a tuple of two numpy arrays representing slope and curvature (1st grade derivative and 2nd grade derivative)

    Args:
        dem: input numpy array
        slope_cellsize: window size to calculate slope and curvature
        title: array name

    Returns:
        tuple of ndarrays: slope image, curvature image

    """

    app_logger.info(f"dem shape:{dem.shape}, slope_cellsize:{slope_cellsize}.")

    try:
        dem = dem.astype(float)
        app_logger.debug("get_slope_curvature:: start")
        slope = calculate_slope(dem, slope_cellsize)
        app_logger.debug("get_slope_curvature:: created slope raster")
        s2c = calculate_slope(slope, slope_cellsize)
        curvature = normalize_array(s2c, norm_type="float", title=f"SC:curvature_{title}")
        app_logger.debug("get_slope_curvature:: created curvature raster")

        return slope, curvature
    except ValueError as ve_get_slope_curvature:
        msg = f"ve_get_slope_curvature:{ve_get_slope_curvature}."
        app_logger.error(msg)
        raise ve_get_slope_curvature


def calculate_slope(dem_array: ndarray, cell_size: int, calctype: str = "degree") -> ndarray:
    """
    Return a numpy array representing slope (1st grade derivative)

    Args:
        dem_array: input numpy array
        cell_size: window size to calculate slope
        calctype: calculus type

    Returns:
        ndarray: slope image

    """

    try:
        gradx, grady = np.gradient(dem_array, cell_size)
        dem_slope = np.sqrt(gradx ** 2 + grady ** 2)
        if calctype == "degree":
            dem_slope = np.degrees(np.arctan(dem_slope))
        app_logger.debug(f"extracted slope with calctype:{calctype}.")
        return dem_slope
    except ValueError as ve_calculate_slope:
        msg = f"ve_calculate_slope:{ve_calculate_slope}."
        app_logger.error(msg)
        raise ve_calculate_slope


def normalize_array(arr: ndarray, high: int = 255, norm_type: str = "float", invert: bool = False, title: str = "") -> ndarray:
    """
    Return normalized numpy array between 0 and 'high' value. Default normalization type is int
    
    Args:
        arr: input numpy array
        high: max value to use for normalization
        norm_type: type of normalization: could be 'float' or 'int'
        invert: bool to choose if invert the normalized numpy array
        title: array title name

    Returns:
        ndarray: normalized numpy array

    """

    h_min_arr = np.nanmin(arr)
    h_arr_max = np.nanmax(arr)
    try:
        h_diff = h_arr_max - h_min_arr
        app_logger.debug(
            f"normalize_array:: '{title}',h_min_arr:{h_min_arr},h_arr_max:{h_arr_max},h_diff:{h_diff}, dtype:{arr.dtype}.")
    except Exception as e_h_diff:
        app_logger.error(f"e_h_diff:{e_h_diff}.")
        raise e_h_diff

    if check_empty_array(arr, high) or check_empty_array(arr, h_diff):
        msg_ve = f"normalize_array::empty array '{title}',h_min_arr:{h_min_arr},h_arr_max:{h_arr_max},h_diff:{h_diff}, dtype:{arr.dtype}."
        app_logger.error(msg_ve)
        raise ValueError(msg_ve)
    try:
        normalized = high * (arr - h_min_arr) / h_diff
        normalized = np.nanmax(normalized) - normalized if invert else normalized
        return normalized.astype(int) if norm_type == "int" else normalized
    except FloatingPointError as fe:
        msg = f"normalize_array::{title}:h_arr_max:{h_arr_max},h_min_arr:{h_min_arr},fe:{fe}."
        app_logger.error(msg)
        raise ValueError(msg)


def normalize_array_list(arr_list: list[ndarray], exaggerations_list: list[float] = None, title: str = "") -> ndarray:
    """
    Return a normalized numpy array from a list of numpy array and an optional list of exaggeration values.
    
    Args:
        arr_list: list of array to use for normalization
        exaggerations_list: list of exaggeration values
        title: array title name

    Returns:
        ndarray: normalized numpy array

    """

    if not arr_list:
        msg = f"input list can't be empty:{arr_list}."
        app_logger.error(msg)
        raise ValueError(msg)
    if exaggerations_list is None:
        exaggerations_list = list(np.ones(len(arr_list)))
    arr_tmp = np.zeros(arr_list[0].shape)
    for a, exaggeration in zip(arr_list, exaggerations_list):
        app_logger.debug(f"normalize_array_list::exaggeration:{exaggeration}.")
        arr_tmp += normalize_array(a, norm_type="float", title=f"ARRLIST:{title}.") * exaggeration
    return arr_tmp / len(arr_list)


def check_empty_array(arr: ndarray, val: float) -> bool:
    """
    Return True if the input numpy array is empy. Check if
        - all values are all the same value (0, 1 or given 'val' input float value)
        - all values that are not NaN are a given 'val' float value

    Args:
        arr: input numpy array
        val: value to use for check if array is empty

    Returns:
        bool: True if the input numpy array is empty, False otherwise

    """

    arr_check5_tmp = np.copy(arr)
    arr_size = arr.shape[0]
    arr_check3 = np.ones((arr_size, arr_size))
    check1 = np.array_equal(arr, arr_check3)
    check2 = np.array_equal(arr, np.zeros((arr_size, arr_size)))
    arr_check3 *= val
    check3 = np.array_equal(arr, arr_check3)
    arr[np.isnan(arr)] = 0
    check4 = np.array_equal(arr, np.zeros((arr_size, arr_size)))
    arr_check5 = np.ones((arr_size, arr_size)) * val
    arr_check5_tmp[np.isnan(arr_check5_tmp)] = val
    check5 = np.array_equal(arr_check5_tmp, arr_check5)
    app_logger.debug(f"array checks:{check1}, {check2}, {check3}, {check4}, {check5}.")
    return check1 or check2 or check3 or check4 or check5
