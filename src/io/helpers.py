"""Helpers dedicated to georeferencing duties"""
import base64
import glob
import json
import os
import zlib
from math import log, tan, radians, cos, pi, floor, degrees, atan, sinh

import rasterio

from src import app_logger
from src.utilities.constants import GEOJSON_SQUARE_TEMPLATE, OUTPUT_CRS_STRING, INPUT_CRS_STRING, SKIP_CONDITIONS_LIST
from src.utilities.type_hints import ts_llist_float2, ts_geojson, ts_dict_str2b, ts_tuple_flat2, ts_tuple_flat4, \
    ts_list_float4, ts_llist2, ts_tuple_int4, ts_ddict2

ZIPJSON_KEY = 'base64(zip(o))'


def get_geojson_square_angles(bounding_box:ts_llist_float2, name:str="buffer", debug:bool=False) -> ts_geojson:
    """
    Create a geojson-like dict rectangle from the input latitude/longitude bounding box
    
    Args:
        bounding_box: float latitude/longitude bounding box
        name: geojson-like rectangle name
        debug: bool, default=False
            logging debug argument

    Returns:
        dict: geojson-like object rectangle
        
    """
    import copy
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)
    app_logger.info(f"bounding_box:{bounding_box}.")
    top = bounding_box[0][0]
    right = bounding_box[0][1]
    bottom = bounding_box[1][0]
    left = bounding_box[1][1]
    bottom_left = [left, bottom]
    top_left = [left, top]
    top_right = [right, top]
    bottom_right = [right, bottom]
    coords = [bottom_left, top_left, top_right, bottom_right]
    app_logger.info(f"coords:{coords}.")
    geojson = copy.copy(GEOJSON_SQUARE_TEMPLATE)
    geojson["name"] = name
    geojson["features"][0]["geometry"]["coordinates"] = [[coords]]
    app_logger.info(f"geojson:{geojson}.")
    return geojson


def crop_raster(merged_raster_path:str, area_crop_geojson:dict, debug:bool=False) -> ts_dict_str2b:
    """
    Crop a raster using a geojson-like object rectangle
    
    Args:
        merged_raster_path: filename path pointing string to the raster to crop
        area_crop_geojson: geojson-like object rectangle
        debug: bool, default=False
            logging debug argument

    Returns:
        dict: the cropped raster numpy array and the transform object with the georeferencing reference

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)
    try:
        import rasterio
        from rasterio.mask import mask

        app_logger.info(f"area_crop_geojson::{area_crop_geojson}.")
        geojson_reprojected = get_geojson_reprojected(area_crop_geojson, debug=debug)
        shapes = [feature["geometry"] for feature in geojson_reprojected["features"]]
        app_logger.info(f"geojson_reprojected:{geojson_reprojected}.")

        app_logger.info(f"reading merged_raster_path while masking it from path:{merged_raster_path}.")
        with rasterio.open(merged_raster_path, "r") as src:
            masked_raster, masked_transform = mask(src, shapes, crop=True)
            masked_meta = src.meta
            app_logger.info(f"merged_raster_path, src:{src}.")
        masked_meta.update({
            "driver": "GTiff", "height": masked_raster.shape[1],
            "width": masked_raster.shape[2], "transform": masked_transform}
        )
        return {"masked_raster": masked_raster, "masked_meta": masked_meta, "masked_transform": masked_transform}
    except Exception as e:
        app_logger.error(e)
        raise e


def get_geojson_reprojected(geojson:dict, output_crs:str=OUTPUT_CRS_STRING, debug:bool=False) -> dict:
    """
    change projection for input geojson-like object polygon

    Args:
        geojson: input geojson-like object polygon
        output_crs: output crs string - Coordinate Reference Systems
        debug: logging debug argument

    Returns:
        dict: reprojected geojson-like object

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)
    if not isinstance(geojson, dict):
        raise ValueError(f"geojson here should be a dict, not of type {type(geojson)}.")
    app_logger.info(f"start reprojecting geojson:{geojson}.")
    try:
        features = geojson['features']

        output_crs_json = {"type": "name", "properties": {"name": f"urn:ogc:def:crs:{output_crs}"}}
        geojson_output = {'features': [], 'type': 'FeatureCollection', "name": "converted", "crs": output_crs_json}

        # Iterate through each feature of the feature collection
        for feature in features:
            feature_out = feature.copy()
            new_coords = []
            feat = feature['geometry']
            app_logger.info(f"feat:{feat}.")
            coords = feat['coordinates']
            app_logger.info(f"coordinates:{coords}.")
            # iterate over "coordinates" lists with 3 nested loops, practically with only one element but last loop
            for coord_a in coords:
                new_coords_a = []
                for cord_b in coord_a:
                    new_coords_b = []
                    # Project/transform coordinate pairs of each ring
                    # (iteration required in case geometry type is MultiPolygon, or there are holes)
                    for xconv, yconf in cord_b:
                        app_logger.info(f"xconv, yconf:{xconv},{yconf}.")
                        x2, y2 = latlon_to_mercator(xconv, yconf)
                        app_logger.info(f"x2, y2:{x2},{y2}.")
                        new_coords_b.append([x2, y2])
                    new_coords_a.append(new_coords_b)
                new_coords.append(new_coords_a)
            feature_out['geometry']['coordinates'] = new_coords
            geojson_output['features'].append(feature_out)
        app_logger.info(f"geojson_output:{geojson_output}.")
        return geojson_output
    except KeyError as ke_get_geojson_reprojected:
        msg = f"ke_get_geojson_reprojected:{ke_get_geojson_reprojected}."
        app_logger.error(msg)
        raise KeyError(msg)


def latlon_to_mercator(
        lat:float, lon:float, input_crs:str=INPUT_CRS_STRING, output_crs:str=OUTPUT_CRS_STRING, always_xy:bool=True, debug:bool=False
) -> ts_tuple_flat2:
    """
    Return a tuple of latitude, longitude float coordinates values transformed to mercator

    Args:

        lat: input latitude float value
        lon: input longitude float value
        input_crs: string, input Coordinate Reference Systems
        output_crs: string, output Coordinate Reference Systems
        always_xy: bool, default=True. 
            If true, the transform method will accept as input and return as output
            coordinates using the traditional GIS order, that is longitude, latitude
            for geographic CRS and easting, northing for most projected CRS.
        debug: bool, default=False.
            logging debug argument

    Returns:
        tuple latitude/longitude float values

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging
    #app_logger = setup_logging(debug)
    try:
        from pyproj import Transformer
        app_logger.info(f"lat:{lat},lon:{lon}.")
        transformer = Transformer.from_crs(input_crs, output_crs, always_xy=always_xy)
        out_lat, out_lon = transformer.transform(lat, lon)
        app_logger.info(f"out_lat:{out_lat},out_lon:{out_lon}.")
        return out_lat, out_lon
    except Exception as e_latlon_to_mercator:
        app_logger.error(f"e_latlon_to_mercator:{e_latlon_to_mercator}.")
        raise e_latlon_to_mercator


def sec(x:float) -> float:
    """
    Return secant (the reciprocal of the cosine) for given value

    Args:
        x: input float value

    Returns:
        float: secant of given float value

    """
    return 1 / cos(x)


def latlon_to_xyz(lat:float, lon:float, z:int) -> ts_tuple_flat2:
    """
    Return x/y coordinates points for tiles from latitude/longitude values point.

    Args:
        lon: float longitude value
        lat: float latitude value
        z: float zoom value

    Returns:
        tuple: x, y values tiles coordinates

    """
    tile_count = pow(2, z)
    x = (lon + 180) / 360
    y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
    return tile_count * x, tile_count * y


def bbox_to_xyz(lon_min:float, lon_max:float, lat_min:float, lat_max:float, z:int) -> ts_tuple_flat4:
    """
    Return xyz reference coordinates for tiles from latitude/longitude min and max values.

    Args:
        lon_min: float min longitude value
        lon_max: float max longitude value
        lat_min: float min latitude value
        lat_max: float max latitude value
        z: float zoom value

    Returns:
        tuple: float x min, x max, y min, y max values tiles coordinates

    """
    x_min, y_max = latlon_to_xyz(lat_min, lon_min, z)
    x_max, y_min = latlon_to_xyz(lat_max, lon_max, z)
    return (floor(x_min), floor(x_max),
            floor(y_min), floor(y_max))


def mercator_to_lat(mercator_y:float) -> float:
    """
    Return latitude value coordinate from mercator coordinate value

    Args:
        mercator_y: float mercator value coordinate

    Returns:
        float: latitude value coordinate

    """
    return degrees(atan(sinh(mercator_y)))


def y_to_lat_edges(y:float, z:int) -> ts_tuple_flat2:
    """
    Return edge float latitude values coordinates from x,z tiles coordinates

    Args:
        y: float x tile value coordinate
        z: float zoom tile value coordinate

    Returns:
        tuple: two float latitude values coordinates

    """
    tile_count = pow(2, z)
    unit = 1 / tile_count
    relative_y1 = y * unit
    relative_y2 = relative_y1 + unit
    lat1 = mercator_to_lat(pi * (1 - 2 * relative_y1))
    lat2 = mercator_to_lat(pi * (1 - 2 * relative_y2))
    return lat1, lat2


def x_to_lon_edges(x:float, z:int) -> ts_tuple_flat2:
    """
    Return edge float longitude values coordinates from x,z tiles coordinates

    Args:
        x: float x tile value coordinate
        z: float zoom tile value coordinate

    Returns:
        tuple: two float longitude values coordinates

    """
    tile_count = pow(2, z)
    unit = 360 / tile_count
    lon1 = -180 + x * unit
    lon2 = lon1 + unit
    return lon1, lon2


def tile_edges(x:float, y:float, z:int) -> ts_list_float4:
    """
    Return edge float latitude/longitude value coordinates from xyz tiles coordinates

    Args:
        x: float x tile value coordinate
        y: float y tile value coordinate
        z: float zoom tile value coordinate

    Returns:
        tuple: float latitude/longitude values coordinates

    """
    lat1, lat2 = y_to_lat_edges(y, z)
    lon1, lon2 = x_to_lon_edges(x, z)
    return [lon1, lat1, lon2, lat2]


def merge_tiles(input_pattern:str, output_path:str, temp_dir:str, debug:bool=False) -> None:
    """
    Merge given raster glob input pattern into one unique georeferenced raster.

    Args:
        input_pattern: input glob pattern needed for search the raster filenames
        output_path: output path where to write the merged raster
        temp_dir: temporary folder needed for create
        debug: bool, default=False.
            logging debug argument

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)
    try:
        from osgeo import gdal
    except ModuleNotFoundError as module_error_merge_tiles:
        msg = f"module_error_merge_tiles:{module_error_merge_tiles}."
        app_logger.error(msg)
        raise module_error_merge_tiles

    try:
        vrt_path = os.path.join(temp_dir, "tiles.vrt")
        os_list_dir1 = os.listdir(temp_dir)
        app_logger.info(f"os_list_dir1:{os_list_dir1}.")

        gdal.BuildVRT(vrt_path, glob.glob(input_pattern))
        gdal.Translate(output_path, vrt_path)

        os_list_dir2 = os.listdir(temp_dir)
        app_logger.info(f"os_list_dir2:{os_list_dir2}.")
    except IOError as ioe_merge_tiles:
        msg = f"ioe_merge_tiles:{ioe_merge_tiles}."
        app_logger.error(msg)
        raise ioe_merge_tiles


def get_lat_lon_coords(bounding_box: ts_llist2) -> ts_tuple_int4:
    """
    Return couples of float latitude/longitude values from bounding box input list.

    Args:
        bounding_box: bounding box input list of latitude/longitude coordinates

    Returns:
        tuple: float longitude min, latitude min, longitude max, longitude max values coordinates

    """
    top_right, bottom_left = bounding_box
    lat_max, lon_max = top_right
    lat_min, lon_min = bottom_left
    if lon_min == lon_max or lat_min == lat_max:
        raise ValueError(f"latitude and/or longitude coordinates should not be equal each others... {bounding_box}.")
    return lon_min, lat_min, lon_max, lat_max


def get_prediction_georeferenced(prediction_obj:dict, transform:rasterio.transform, skip_conditions_list:list=None, debug:bool=False) -> dict:
    """
    Return a georeferenced geojson-like object starting from a dict containing "predictions" -> "points" list.
    Apply the affine transform matrix of georeferenced raster submitted to the machine learning model.  

    Args:
        prediction_obj: input dict 
        transform: 'rasterio.transform' or dict list, affine tranform matrix
        skip_conditions_list: dict list, skip condition list
        debug: bool, default=False.
            logging debug argument

    Returns:
        dict

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    if skip_conditions_list is None:
        skip_conditions_list = SKIP_CONDITIONS_LIST

    #app_logger = setup_logging(debug)
    app_logger.info(f"prediction_obj::{prediction_obj}, transform::{transform}.")
    crs = {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::3857"}}
    geojson_obj = {'features': [], 'type': 'FeatureCollection', "name": "geojson_name", "crs": crs}
    for n, prediction in enumerate(prediction_obj["predictions"]):
        points_dict_ = prediction["points"]
        points_list = [[p["x"], p["y"]] for p in points_dict_]
        app_logger.info(f"points_list::{points_list}.")
        # if check_skip_conditions(prediction, skip_conditions_list, debug=debug):
        #     continue
        feature = populate_features_geojson(n, points_list, confidence=prediction["confidence"], geomorphic_class=prediction["class"])
        app_logger.info(f"geojson::feature:{feature}.")
        feature["geometry"] = apply_transform(feature["geometry"], transform, debug=debug)
        geojson_obj["features"].append(feature)
    app_logger.info(f"geojson::post_update:{geojson_obj}.")
    return geojson_obj


def populate_features_geojson(idx: int, coordinates_list: list, **kwargs) -> ts_ddict2:
    """
    Return a list of coordinate points in a geojson-like feature-like object.

    Args:
        idx: int, feature index
        coordinates_list: dict list, coordinate points
        **kwargs: optional arguments to merge within the geojson properties feature

    Returns:
        dict

    """
    return {
        "type": "Feature",
        "properties": {"id": idx, **kwargs},
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": [[coordinates_list]],
        }
    }


def check_skip_conditions(prediction:dict, skip_conditions_list:list, debug:bool=False) -> bool:
    """
    Loop over elements within skip_condition_list and return a boolean if no condition to skip (or exceptions).

    Args:
        prediction: input dict to check
        skip_conditions_list: dict list with conditions to evaluate
        debug: bool, default=False
            logging debug argument

    Returns:
        bool

    """
    for obj in skip_conditions_list:
        return skip_feature(prediction, obj["skip_key"], obj["skip_value"], obj["skip_condition"], debug=debug)
    return False


def skip_feature(prediction:dict, skip_key:float, skip_value:str, skip_condition:str, debug:bool=False) -> bool:
    """
    Return False if values from input dict shouldn't be skipped,
    True in case of exceptions, empty skip_condition or when chosen condition meets skip_value and skip_condition.

    E.g. confidence should be major than 0.8: if confidence is equal to 0.65 then return True (0.65 < 0.8) and skip!

    Args:
        prediction: input dict to check
        skip_key: skip condition key string
        skip_value: skip condition value string
        skip_condition: string (major | minor | equal)
        debug: bool, default=False
            logging debug argument

    Returns:
        bool

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging
    #app_logger = setup_logging(debug)
    try:
        v = prediction[skip_key]
        match skip_condition:
            case "major":
                return v > skip_value
            case "minor":
                return v < skip_value
            case "equal":
                return v == skip_value
            case "":
                return False
    except KeyError as ke_filter_feature:
        app_logger.error(f"ke_filter_feature:{ke_filter_feature}.")
        return False
    except Exception as e_filter_feature:
        app_logger.error(f"e_filter_feature:{e_filter_feature}.")
        return False


def apply_transform(geometry:object, transform:list[object], debug:bool=False) -> dict:
    """
    Returns a GeoJSON-like mapping from a transformed geometry using an affine transformation matrix.

    The coefficient matrix is provided as a list or tuple with 6 items
    for 2D transformations. The 6 parameter matrix is::

        [a, b, d, e, xoff, yoff]

    which represents the augmented matrix::

        [x']   / a  b xoff \ [x]
        [y'] = | d  e yoff | [y]
        [1 ]   \ 0  0   1  / [1]

    or the equations for the transformed coordinates::

        x' = a * x + b * y + xoff
        y' = d * x + e * y + yoff

    Args:
        geometry: geometry value from a geojson dict
        transform: list of float values (affine transformation matrix)
        debug: bool, default=False
            logging debug argument

    Returns:
        dict

    """
    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)

    try:
        from shapely.affinity import affine_transform
        from shapely.geometry import mapping, shape
        try:
            geometry_transformed = affine_transform(shape(geometry), [transform.a, transform.b, transform.d, transform.e, transform.xoff, transform.yoff])
        except AttributeError as ae:
            app_logger.warning(f"ae:{ae}.")
            geometry_transformed = affine_transform(shape(geometry), [transform[0], transform[1], transform[2], transform[3], transform[4], transform[5]])
        geometry_serialized = mapping(geometry_transformed)
        app_logger.info(f"geometry_serialized:{geometry_serialized}.")
        return geometry_serialized
    except ImportError as ie_apply_transform:
        app_logger.error(f"ie_apply_transform:{ie_apply_transform}.")
        raise ie_apply_transform
    except Exception as e_apply_transform:
        app_logger.error(f"e_apply_transform:{e_apply_transform}.")
        raise e_apply_transform


def get_perc(nan_count:int, total_count:int) -> str:
    """
    Return a formatted string with a percentage value representing the ratio between NaN and total number elements within a numpy array

    Args:
        nan_count: NaN value elements
        total_count: total count of elements

    Returns:
        str

    """
    return f"{100*nan_count/total_count:.2f}"


def json_unzip(j:dict, debug:bool=False) -> str:
    """
    Return uncompressed content from input dict using 'zlib' library

    Args:
        j: input dict to uncompress. key must be 'base64(zip(o))'
        debug: logging debug argument

    Returns:
        dict: uncompressed dict

    """
    from json import JSONDecodeError
    from zlib import error as zlib_error

    #from src.surferdtm_prediction_api.utilities.utilities import setup_logging

    #app_logger = setup_logging(debug)

    try:
        j = zlib.decompress(base64.b64decode(j[ZIPJSON_KEY]))
    except KeyError as ke:
        ke_error_msg = f"Could not decode/unzip the content because of wrong/missing dict key:{ke}."
        raise KeyError(ke_error_msg)
    except zlib_error as zlib_error2:
        zlib_error2_msg = f"Could not decode/unzip the content because of:{zlib_error2}."
        app_logger.error(zlib_error2_msg)
        raise RuntimeError(zlib_error2_msg)

    try:
        j = json.loads(j)
    except JSONDecodeError as json_e1:
        msg = f"Could interpret the unzipped content because of JSONDecodeError with msg:{json_e1.msg}, pos:{json_e1.pos}, broken json:'{json_e1.doc}'"
        app_logger.error(msg)
        raise RuntimeError(msg)

    return j


def json_zip(j:dict) -> dict[str]:
    """
    Return compressed content from input dict using 'zlib' library

    Args:
        j: input dict to compress

    Returns:
        dict: compressed dict

    """
    return {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(
                json.dumps(j).encode('utf-8')
            )
        ).decode('ascii')
    }
