import json
import logging
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from samgis_web.utilities.local_tiles_http_server import LocalTilesHttpServer
from samgis_web.web import web_helpers
from . import test_client_health

import app


infer_samgis = "/infer_samgis"
response_status_code = "response.status_code:{}."
response_body_loaded = "response.body_loaded:{}."
client = TestClient(app.app)
source = {
    'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', 'max_zoom': 19,
    'html_attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    'attribution': '(C) OpenStreetMap contributors', 'name': 'OpenStreetMap.Mapnik'
}
event = {
    "bbox": {
        "ne": {"lat": 39.036252959636606, "lng": 15.040283203125002},
        "sw": {"lat": 38.302869955150044, "lng": 13.634033203125002}
    },
    "prompt": [{"type": "point", "data": {"lat": 38.48542007717153, "lng": 14.921846904165468}, "label": 0}],
    "zoom": 10, "source_type": "OpenStreetMap"
}
response_bodies_post_test = {
    "single_point": {
        'bbox': [[39.036252959636606, 15.040283203125002], [38.302869955150044, 13.634033203125002]],
        'prompt': [{'type': 'point', 'label': 0, 'data': [937, 514]}], 'zoom': 10,
        'source': source
    },
    "multi_prompt": {
        'bbox': [[39.011714588834074, 15.093841552734377], [38.278078995562105, 13.687591552734377]],
        'prompt': [
            {'type': 'point', 'label': 1, 'data': [839, 421]},
            {'type': 'point', 'label': 1, 'data': [906, 489]},
            {'type': 'point', 'label': 1, 'data': [936, 580]}
        ], 'zoom': 10,
        'source': source
    },
    "single_rectangle": {
        'bbox': [[39.011714588834074, 15.093841552734377], [38.278078995562105, 13.687591552734377]],
        'prompt': [{'type': 'rectangle', 'data': [875, 445, 951, 538]}], 'zoom': 10,
        'source': source
    }
}


def check_body(body: dict, expected_body: dict):
    if body != expected_body:
        logging.error(f"Wrong test: body not {body}.")
        raise ValueError(f"Wrong body: '{body}'")


class TestFastapiApp(unittest.TestCase):
    def test_fastapi_handler_health_200(self):
        response = client.get("/health")
        test_client_health.check_for_statuscode(response.status_code, 200, response)
        body = response.json()
        check_body(body, {"msg": "still alive..."})

    def test_404(self):
        response = client.get("/404")
        test_client_health.check_for_statuscode(response.status_code, 404, response)

    def test_infer_samgis_empty_body_422(self):
        response = client.post(infer_samgis, json={})
        print(response_status_code.format(response.status_code))
        test_client_health.check_for_statuscode(response.status_code, 422, response)
        body = response.json()
        logging.info(response_body_loaded.format(body))
        check_body(body, {"msg": "Error - Unprocessable Entity"})

    def test_infer_samgis_source_422(self):
        from copy import deepcopy
        local_event = deepcopy(event)

        local_event["source_type"] = "source_fake"
        response = client.post(infer_samgis, json=local_event)
        logging.info(response_status_code.format(response.status_code))
        test_client_health.check_for_statuscode(response.status_code, 422, response)
        body = response.json()
        logging.info(response_body_loaded.format(body))
        check_body(body, {"msg": "Error - Unprocessable Entity"})

    @patch.object(app, "samexporter_predict")
    def test_infer_samgis_500(self, samexporter_predict_mocked):
        samexporter_predict_mocked.side_effect = ValueError("I raise a value error!")

        response = client.post(infer_samgis, json=event)
        logging.info(response_status_code.format(response.status_code))
        test_client_health.check_for_statuscode(response.status_code, 500, response)
        body = response.json()
        logging.info(response_body_loaded.format(body))
        check_body(body, {"msg": "Error - Internal Server Error"})

    @patch.object(web_helpers, "get_url_tile")
    @patch.object(time, "time")
    def test_infer_samgis_real_200(self, time_mocked, get_url_tile_mocked):
        import shapely
        import xyzservices
        from tests import LOCAL_URL_TILE, TEST_EVENTS_FOLDER

        time_mocked.return_value = 0
        listen_port = 8000

        local_tile_provider = xyzservices.TileProvider(name="local_tile_provider", url=LOCAL_URL_TILE, attribution="")
        get_url_tile_mocked.return_value = local_tile_provider

        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            response = client.post(infer_samgis, json=event)
            logging.info(response_status_code.format(response.status_code))
        test_client_health.check_for_statuscode(response.status_code, 200, response)
        body_string = response.json()["body"]
        body_loaded = json.loads(body_string)
        logging.info(response_body_loaded.format(body_loaded))
        if "duration_run" not in body_loaded:
            raise ValueError("Missing value in body")
        output = body_loaded["output"]
        if not ('n_predictions' in output and "n_shapes_geojson" in output):
            raise ValueError("Missing value in body")
        geojson = output["geojson"]
        output_geojson = shapely.from_geojson(geojson)
        logging.info("output_geojson::{}.".format(output_geojson))
        if not isinstance(output_geojson, shapely.GeometryCollection):
            raise ValueError("geojson isn't a shapely.GeometryCollection instance")
        if len(output_geojson.geoms) < 2:
            raise ValueError("Less than 2 geometries within the Shapely geometry from the geojson")

    @patch.object(time, "time")
    @patch.object(app, "samexporter_predict")
    def test_infer_samgis_mocked_200(self, samexporter_predict_mocked, time_mocked):
        self.maxDiff = None

        time_mocked.return_value = 0
        samexporter_output = {
          "n_predictions": 1,
          "geojson": "{\"type\": \"FeatureCollection\", \"features\": [{\"id\": \"0\", \"type\": \"Feature\", " +
                     "\"properties\": {\"raster_val\": 255.0}, \"geometry\": {\"type\": \"Polygon\", " +
                     "\"coordinates\": [[[148.359375, -40.4469470596005], [148.447265625, -40.4469470596005], " +
                     "[148.447265625, -40.51379915504414], [148.359375, -40.4469470596005]]]}}]}",
          "n_shapes_geojson": 2
        }
        samexporter_predict_mocked.return_value = samexporter_output

        response = client.post(infer_samgis, json=event)
        logging.info(response_status_code.format(response.status_code))
        test_client_health.check_for_statuscode(response.status_code, 200, response)
        response_json = response.json()
        body_loaded = json.loads(response_json["body"])
        logging.info(response_body_loaded.format(body_loaded))
        self.assertDictEqual(body_loaded, {'duration_run': 0, 'output': samexporter_output})
