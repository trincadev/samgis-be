"""Project constants"""
CHANNEL_EXAGGERATIONS_LIST = [2.5, 1.1, 2.0]
INPUT_CRS_STRING = "EPSG:3857"
OUTPUT_CRS_STRING = "EPSG:4326"
ROOT = "/tmp"
NODATA_VALUES = -32768
SKIP_CONDITIONS_LIST = [{"skip_key": "confidence", "skip_value": 0.5, "skip_condition": "major"}]
FEATURE_SQUARE_TEMPLATE = [
    {'type': 'Feature', 'properties': {'id': 1},
     'geometry': {
         'type': 'MultiPolygon',
         'coordinates': [[]]
     }}
]
GEOJSON_SQUARE_TEMPLATE = {
    'type': 'FeatureCollection', 'name': 'etna_wgs84p',
    'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
    'features': FEATURE_SQUARE_TEMPLATE
}
CUSTOM_RESPONSE_MESSAGES = {
    200: "ok",
    422: "Missing required parameter",
    500: "Internal server error"
}
MODEL_ENCODER_NAME = "mobile_sam.encoder.onnx"
MODEL_DECODER_NAME = "sam_vit_h_4b8939.decoder.onnx"
ZOOM = 13
SOURCE_TYPE = "Satellite"
TILE_SIZE = 256
EARTH_EQUATORIAL_RADIUS = 6378137.0
DEFAULT_TMS = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
WKT_3857 = 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
WKT_3857 += 'AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],'
WKT_3857 += 'PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4",'
WKT_3857 += '"+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs"],AUTHORITY["EPSG","3857"]]'
