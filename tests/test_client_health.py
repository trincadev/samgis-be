import http
import logging
import unittest

from http import client
from httpx import HTTPError, Response
from samgis_web.utilities.local_tiles_http_server import LocalTilesHttpServer

from scripts import client_health
from tests import TEST_EVENTS_FOLDER


def check_for_statuscode(status_code: int, expected_status_code: int | None, response: client.HTTPResponse | Response):
    if status_code != expected_status_code:
        logging.error(f"Wrong test: response not {expected_status_code}.")
        logging.error(response)
        raise HTTPError(f"Wrong test: response has not {expected_status_code}.")


class TestClientHealth(unittest.TestCase):
    def test_get_health_200(self):
        with LocalTilesHttpServer.http_server("localhost", 8000, directory=TEST_EVENTS_FOLDER):
            status_code, response = client_health.get_health("http://localhost:8000/")
            check_for_statuscode(status_code, 200, response)

    def test_get_health_404(self):
        with LocalTilesHttpServer.http_server("localhost", 8000, directory=TEST_EVENTS_FOLDER):
            status_code, response = client_health.get_health("http://localhost:8000/404")
            check_for_statuscode(status_code, 404, response)

    def test_get_health_connection_error(self):
        status_code_500, response_500 = client_health.get_health("http://localhost:8000/")
        check_for_statuscode(status_code_500, None, response_500)


if __name__ == "__main__":
    unittest.main()
