"""Project constants"""
import os


INPUT_CRS_STRING = "EPSG:4326"
OUTPUT_CRS_STRING = "EPSG:3857"
DRIVER_RASTERIO_GTIFF = "GTiff"
ROOT = "/tmp"
CUSTOM_RESPONSE_MESSAGES = {
    200: "ok",
    400: "Bad Request",
    422: "Missing required parameter",
    500: "Internal server error"
}
TILE_SIZE = 256
EARTH_EQUATORIAL_RADIUS = 6378137.0
WKT_3857 = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,'
WKT_3857 += 'AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],'
WKT_3857 += 'UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],'
WKT_3857 += 'PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],'
WKT_3857 += 'PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
WKT_3857 += 'AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 '
WKT_3857 += '+x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'
SERVICE_NAME = "sam-gis"
DEFAULT_LOG_LEVEL = 'INFO'
RETRY_DOWNLOAD = 3
TIMEOUT_DOWNLOAD = 60
CALLBACK_INTERVAL_DOWNLOAD = 0.05
BOOL_USE_CACHE = True
N_WAIT = 0
N_MAX_RETRIES = 2
N_CONNECTION = 2
ZOOM_AUTO = "auto"
DEFAULT_URL_TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
DOMAIN_URL_TILES_MAPBOX = "api.mapbox.com"
RELATIVE_URL_TILES_MAPBOX = "v/mapbox.terrain-rgb/{zoom}/{x}/{y}{@2x}.pngraw?access_token={TOKEN}"
COMPLETE_URL_TILES_MAPBOX = f"https://{DOMAIN_URL_TILES_MAPBOX}/{RELATIVE_URL_TILES_MAPBOX}"
# https://s3.amazonaws.com/elevation-tiles-prod/terrarium/13/1308/3167.png
DOMAIN_URL_TILES_NEXTZEN = "s3.amazonaws.com"
RELATIVE_URL_TILES_NEXTZEN = "elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"  # "terrarium/{z}/{x}/{y}.png"
COMPLETE_URL_TILES_NEXTZEN = f"https://{DOMAIN_URL_TILES_NEXTZEN}/{RELATIVE_URL_TILES_NEXTZEN}"
CHANNEL_EXAGGERATIONS_LIST = [2.5, 1.1, 2.0]
SLOPE_CELLSIZE = 61
MODEL_NAME = os.getenv("MODEL_NAME", "mobile_sam")