import unittest

import numpy as np

from src import app_logger
from src.io.tms2geotiff import download_extent
from src.utilities.utilities import hash_calculate
from tests import LOCAL_URL_TILE, TEST_EVENTS_FOLDER


input_bbox = [[39.036252959636606, 15.040283203125002], [38.302869955150044, 13.634033203125002]]


class TestTms2geotiff(unittest.TestCase):
    def test_download_extent(self):
        from tests.local_tiles_http_server import LocalTilesHttpServer

        listen_port = 8000

        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10
            img, matrix = download_extent(
                source=LOCAL_URL_TILE, lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
            )
            app_logger.info("# DOWNLOAD ENDED! #")
            np_img = np.array(img)
            output_hash = hash_calculate(np_img)
            assert output_hash == b'Rd95Whd3nP4PW4pgcYsoyTqUUabpt8LfYxns022em7o='
            assert matrix == (1517733.63363046, 152.8740565703522, 0, 4726865.829155299, 0, -152.87405657035038)

    def test_download_extent_io_error1(self):

        with self.assertRaises(IOError):
            try:
                pt0, pt1 = input_bbox
                zoom = 10
                download_extent(
                    source=LOCAL_URL_TILE, lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
                )
            except IOError as ioe1:
                app_logger.error(f"ioe1:{ioe1}.")
                msg0 = "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /lambda_handler"
                msg1 = "Caused by NewConnectionError"
                msg2 = ": Failed to establish a new connection: [Errno 61] Connection refused'))"
                assert msg0 in str(ioe1)
                assert msg1 in str(ioe1)
                assert msg2 in str(ioe1)
                raise ioe1

    def test_download_extent_io_error2(self):
        from tests.local_tiles_http_server import LocalTilesHttpServer

        listen_port = 8000
        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10

            with self.assertRaises(AttributeError):
                try:
                    download_extent(
                        source=LOCAL_URL_TILE + "_not_found_raster!",
                        lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
                    )
                except AttributeError as ae:
                    app_logger.error(f"ae:{ae}.")
                    assert str(ae) == "'NoneType' object has no attribute 'crop'"
                    raise ae
