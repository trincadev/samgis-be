import unittest

import numpy as np

from src import app_logger
from src.io.tms2geotiff import download_extent
from src.utilities.utilities import hash_calculate
from tests import LOCAL_URL_TILE, TEST_EVENTS_FOLDER

input_bbox = [[39.036252959636606, 15.040283203125002], [38.302869955150044, 13.634033203125002]]


class TestTms2geotiff(unittest.TestCase):
    def test_download_extent_simple_source(self):
        from rasterio import Affine
        from xyzservices import TileProvider
        from tests.local_tiles_http_server import LocalTilesHttpServer

        listen_port = 8000

        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10

            n_lat = pt0[0]
            e_lng = pt0[1]
            s_lat = pt1[0]
            w_lng = pt1[1]

            source = TileProvider(name="local_tile_provider", url=LOCAL_URL_TILE, attribution="")
            img, matrix = download_extent(w=w_lng, s=s_lat, e=e_lng, n=n_lat, zoom=zoom, source=source)
            app_logger.info(f"# DOWNLOAD ENDED, shape: {img.shape} #")
            np_img = np.ascontiguousarray(img)
            output_hash = hash_calculate(np_img)
            assert output_hash == b'UmbkwbPJpRT1XXcLnLUapUDP320w7YhS/AmT3H7u+b4='
            assert Affine.to_gdal(matrix) == (
                1517657.1966021745, 152.8740565703525, 0.0, 4726942.266183584, 0.0, -152.87405657034955)

    def test_download_extent_source_with_parameter(self):
        from rasterio import Affine
        from xyzservices import TileProvider
        from tests.local_tiles_http_server import LocalTilesHttpServer

        listen_port = 8000

        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10

            n_lat = pt0[0]
            e_lng = pt0[1]
            s_lat = pt1[0]
            w_lng = pt1[1]

            local_url_tile2 = "http://localhost:8000/{parameter}/{z}/{x}/{y}.png"
            source = TileProvider(
                name="local_tile_provider", url=local_url_tile2, attribution="", parameter="lambda_handler")
            img, matrix = download_extent(w=w_lng, s=s_lat, e=e_lng, n=n_lat, zoom=zoom, source=source)
            app_logger.info(f"# DOWNLOAD ENDED, shape: {img.shape} #")
            np_img = np.ascontiguousarray(img)
            output_hash = hash_calculate(np_img)
            assert output_hash == b'UmbkwbPJpRT1XXcLnLUapUDP320w7YhS/AmT3H7u+b4='
            assert Affine.to_gdal(matrix) == (
                1517657.1966021745, 152.8740565703525, 0.0, 4726942.266183584, 0.0, -152.87405657034955)

    def test_download_extent_source_with_parameter_key_error(self):
        from xyzservices import TileProvider

        with self.assertRaises(KeyError):
            try:
                pt0, pt1 = input_bbox
                zoom = 10

                n_lat = pt0[0]
                e_lng = pt0[1]
                s_lat = pt1[0]
                w_lng = pt1[1]

                local_url_tile2 = "http://localhost:8000/{parameter}/{z}/{x}/{y}.png"
                source = TileProvider(name="local_tile_provider", url=local_url_tile2, attribution="")
                download_extent(w=w_lng, s=s_lat, e=e_lng, n=n_lat, zoom=zoom, source=source)
            except KeyError as ke:
                assert str(ke) == "'parameter'"
                raise ke

    def test_download_extent_io_error1(self):

        with self.assertRaises(Exception):
            try:
                pt0, pt1 = input_bbox
                zoom = 10

                n_lat = pt0[0]
                e_lng = pt0[1]
                s_lat = pt1[0]
                w_lng = pt1[1]

                download_extent(w=w_lng, s=s_lat, e=e_lng, n=n_lat, zoom=zoom, source=f"http://{LOCAL_URL_TILE}")
                print("exception not raised")
            except ConnectionError as ioe1:
                app_logger.error(f"ioe1:{ioe1}.")
                msg0 = "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /lambda_handler"
                msg1 = "Caused by NewConnectionError"
                msg2 = ": Failed to establish a new connection: [Errno 61] Connection refused'))"
                assert msg0 in str(ioe1)
                assert msg1 in str(ioe1)
                assert msg2 in str(ioe1)
                raise ioe1

    def test_download_extent_io_error2(self):
        from requests import HTTPError
        from tests.local_tiles_http_server import LocalTilesHttpServer

        listen_port = 8000
        with LocalTilesHttpServer.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10

            with self.assertRaises(HTTPError):
                try:
                    n_lat = pt0[0]
                    e_lng = pt0[1]
                    s_lat = pt1[0]
                    w_lng = pt1[1]

                    download_extent(w=w_lng, s=s_lat, e=e_lng, n=n_lat, zoom=zoom,
                                    source=LOCAL_URL_TILE + "_not_found_raster!")
                except HTTPError as http_e:
                    app_logger.error(f"ae:{http_e}.")
                    assert "Tile URL resulted in a 404 error. Double-check your tile url:" in str(http_e)
                    raise http_e
