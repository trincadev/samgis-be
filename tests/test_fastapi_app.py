import json
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from samgis import PROJECT_ROOT_FOLDER
from samgis.io import wrappers_helpers
from tests import TEST_EVENTS_FOLDER
from tests.local_tiles_http_server import LocalTilesHttpServer
from wrappers import fastapi_wrapper
from wrappers.fastapi_wrapper import app

client = TestClient(app)
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


class TestFastapiApp(unittest.TestCase):
    def test_fastapi_handler_health_200(self):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body == {"msg": "still alive..."}

    def test_fastapi_handler_post_test_200(self):
        fn_name = "lambda_handler"
        for json_filename in [
            "single_point",
            "multi_prompt",
            "single_rectangle"
        ]:
            with open(TEST_EVENTS_FOLDER / f"{fn_name}_{json_filename}.json") as tst_json:
                inputs_outputs = json.load(tst_json)
                input_body = json.loads(inputs_outputs["input"]["body"])
                response = client.post("/post_test", json=input_body)
                assert response.status_code == 200
                response_body = response.json()
                assert response_body == response_bodies_post_test[json_filename]

    def test_fastapi_handler_post_test_422(self):
        response = client.post("/post_test", json={})
        assert response.status_code == 422
        body = response.json()
        assert body == {'msg': 'Error - Unprocessable Entity'}

    def test_index(self):
        import subprocess

        subprocess.run(["pnpm", "build"], cwd=PROJECT_ROOT_FOLDER / "static")
        subprocess.run(["pnpm", "tailwindcss", "-i", "./src/input.css", "-o", "./dist/output.css"],
                       cwd=PROJECT_ROOT_FOLDER / "static")
        response = client.get("/")
        assert response.status_code == 200
        html_body = response.read().decode("utf-8")
        assert "html" in html_body
        assert "head" in html_body
        assert "body" in html_body

    def test_404(self):
        response = client.get("/404")
        assert response.status_code == 404

    def test_infer_samgis_422(self):
        response = client.post("/infer_samgis", json={})
        print("response.status_code:", response.status_code)
        assert response.status_code == 422
        body_loaded = response.json()
        print("response.body_loaded:", body_loaded)
        assert body_loaded == {"msg": "Error - Unprocessable Entity"}

    def test_infer_samgis_middleware_500(self):
        from copy import deepcopy
        local_event = deepcopy(event)

        local_event["source_type"] = "source_fake"
        response = client.post("/infer_samgis", json=local_event)
        print("response.status_code:", response.status_code)
        assert response.status_code == 500
        body_loaded = response.json()
        print("response.body_loaded:", body_loaded)
        assert body_loaded == {'success': False}

    @patch.object(time, "time")
    @patch.object(fastapi_wrapper, "samexporter_predict")
    def test_infer_samgis_500(self, samexporter_predict_mocked, time_mocked):
        time_mocked.return_value = 0
        samexporter_predict_mocked.side_effect = ValueError("I raise a value error!")

        response = client.post("/infer_samgis", json=event)
        print("response.status_code:", response.status_code)
        assert response.status_code == 500
        body = response.json()
        print("response.body:", body)
        assert body == {'msg': 'Error - Internal Server Error'}

    @patch.object(wrappers_helpers, "get_url_tile")
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
            response = client.post("/infer_samgis", json=event)
            print("response.status_code:", response.status_code)
        assert response.status_code == 200
        body_string = response.json()["body"]
        body_loaded = json.loads(body_string)
        print("response.body_loaded:", body_loaded)
        assert "duration_run" in body_loaded
        output = body_loaded["output"]
        assert 'n_predictions' in output
        assert "n_shapes_geojson" in output
        geojson = output["geojson"]
        output_geojson = shapely.from_geojson(geojson)
        print("output_geojson::", type(output_geojson))
        assert isinstance(output_geojson, shapely.GeometryCollection)
        assert len(output_geojson.geoms) == 3

    @patch.object(time, "time")
    @patch.object(fastapi_wrapper, "samexporter_predict")
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

        response = client.post("/infer_samgis", json=event)
        print("response.status_code:", response.status_code)
        assert response.status_code == 200
        response_json = response.json()
        body_loaded = json.loads(response_json["body"])
        print("response.body_loaded:", body_loaded)
        self.assertDictEqual(body_loaded, {'duration_run': 0, 'output': samexporter_output})
