"""Project constants"""
CHANNEL_EXAGGERATIONS_LIST = [2.5, 1.1, 2.0]
INPUT_CRS_STRING = "EPSG:4326"
OUTPUT_CRS_STRING = "EPSG:3857"
ROOT = "/home/user"
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
