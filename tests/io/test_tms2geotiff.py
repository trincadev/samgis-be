import unittest

import numpy as np

from src import app_logger
from src.io.tms2geotiff import download_extent
from src.utilities.utilities import hash_calculate
from tests import TEST_EVENTS_FOLDER


tile_source_url = "http://localhost:8000/geotiff/{z}/{x}/{y}.tif"
input_bbox = [[38.03932961278458, 15.36808069832851], [37.455509218936974, 14.632807441554068]]


class TestTms2geotiff(unittest.TestCase):
    from contextlib import contextmanager

    @staticmethod
    @contextmanager
    def http_server(host: str, port: int, directory: str):
        """Function http_server defined within this test class to avoid pytest error "fixture 'host' not found"."""
        from functools import partial
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        from threading import Thread

        server = ThreadingHTTPServer(
            (host, port), partial(SimpleHTTPRequestHandler, directory=directory)
        )
        server_thread = Thread(target=server.serve_forever, name="http_server")
        server_thread.start()
        print(f"listen:: host {host}, port {port}.")

        try:
            yield
        finally:
            server.shutdown()
            server_thread.join()

    def test_download_extent(self):
        listen_port = 8000

        with self.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10
            img, matrix = download_extent(
                source=tile_source_url, lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
            )
            app_logger.info("# DOWNLOAD ENDED! #")
            np_img = np.array(img)
            output_hash = hash_calculate(np_img)
            assert output_hash == b'LJNhEuMMp2nRclFJfF6oM3iMVbnZnWDmZqWzrs3T4Hs='

    def test_download_extent_io_error1(self):

        with self.assertRaises(IOError):
            try:
                pt0, pt1 = input_bbox
                zoom = 10
                download_extent(
                    source=tile_source_url, lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
                )
            except IOError as ioe1:
                app_logger.error(f"ioe1:{ioe1}.")
                msg0 = "HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded with url: /geotiff/"
                msg1 = "Caused by NewConnectionError"
                msg2 = ": Failed to establish a new connection: [Errno 61] Connection refused'))"
                assert msg0 in str(ioe1)
                assert msg1 in str(ioe1)
                assert msg2 in str(ioe1)
                raise ioe1

    def test_download_extent_io_error2(self):
        listen_port = 8000
        with self.http_server("localhost", listen_port, directory=TEST_EVENTS_FOLDER):
            pt0, pt1 = input_bbox
            zoom = 10

            with self.assertRaises(AttributeError):
                try:
                    download_extent(
                        source=tile_source_url + "_not_found_raster!",
                        lat0=pt0[0], lon0=pt0[1], lat1=pt1[0], lon1=pt1[1], zoom=zoom
                    )
                except AttributeError as ae:
                    app_logger.error(f"ae:{ae}.")
                    assert str(ae) == "'NoneType' object has no attribute 'crop'"
                    raise ae


if __name__ == '__main__':
    from tests import TEST_ROOT_FOLDER

    main_listen_port = 8000
    print("http_basedir_serve:", TEST_ROOT_FOLDER, "#")
    with TestTms2geotiff.http_server("127.0.0.1", main_listen_port, directory=TEST_ROOT_FOLDER):
        pass
        # import time
        # time.sleep(10)
    print("Http server stopped.")
