import logging
import time
import unittest


class LocalTilesHttpServer(unittest.TestCase):
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
        print("dir:", directory, "#")
        server_thread = Thread(target=server.serve_forever, name="http_server")
        server_thread.start()
        logging.info(f"listen:: host {host}, port {port}.")

        try:
            yield
        finally:
            server.shutdown()
            server_thread.join()


if __name__ == '__main__':
    # from tests import TEST_ROOT_FOLDER
    from pathlib import Path

    PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent

    TEST_ROOT_FOLDER = PROJECT_ROOT_FOLDER / "tests"
    TEST_EVENTS_FOLDER = TEST_ROOT_FOLDER / "events"

    main_listen_port = 8000
    logging.info(f"http_basedir_serve: {TEST_ROOT_FOLDER}.")
    with LocalTilesHttpServer.http_server("localhost", main_listen_port, directory=str(TEST_ROOT_FOLDER)):
        time.sleep(1000)
        logging.info("""import time; time.sleep(10)""")
    # logging.info("Http server stopped.")
