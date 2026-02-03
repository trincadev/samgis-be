#! /usr/bin/env python3

import logging
import sys
from urllib import request
from urllib.error import HTTPError, URLError


DEFAULT_TIMEOUT = 1.5
DEFAULT_SERVER_URL = "http://localhost:7860/health"

logger = logging.Logger("get_health")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def simple_formatter_ex(ex: Exception):
    logger.error(type(ex))
    logger.error(ex)


def get_health(server_url: str = DEFAULT_SERVER_URL, timeout: float = DEFAULT_TIMEOUT) -> tuple[int | None, str]:
    try:
        with request.urlopen(server_url, timeout=timeout) as response:
            logger.warning(f"response type: {type(response)} #")
            logger.debug(msg=response)
            status = response.status
            code = response.code
            logger.warning(f"response status/code: {status}, {code} #")
            html_response =  response.read()
            logger.debug(f"html_response type: {type(html_response)} #")
            logger.debug(html_response)
            html_decoded = html_response.decode("utf8")
            logger.debug(f"html_response type: {type(html_decoded)} #")
            logger.debug(html_decoded)
            return code, html_decoded
    except HTTPError as he:
        logger.error(f"HTTPError: {he.msg} #")
        return he.code, he.msg
    except URLError as ue:
        simple_formatter_ex(ue)
        return ue.errno, str(ue)
    except TimeoutError as te:
        simple_formatter_ex(te)
        return te.errno, str(te)
    except OSError as ose:
        simple_formatter_ex(ose)
        return ose.errno, str(ose)
    except Exception as ex:
        simple_formatter_ex(ex)
        return 500, f"Exception: {repr(ex)} #"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("health checker")
    parser.add_argument(
        "-f", "--server_url", default=DEFAULT_SERVER_URL, nargs="?",
        help=f"Server url string for health GET. Default value: {DEFAULT_SERVER_URL} #"
    )
    parser.add_argument(
        "-t", "--timeout", default=DEFAULT_TIMEOUT, nargs="?",
        help=f"Timeout value for health GET. Default value: {DEFAULT_TIMEOUT}s #"
    )
    args = parser.parse_args()
    logger.warning("arguments: ")
    logger.warning(args)

    status_code, health_response = get_health(server_url=args.server_url, timeout=args.timeout)
    msg = f"status_code: {status_code}"
    msg += " #" if isinstance(status_code, int) else f", {type(status_code)} #"
    logger.warning(msg)
    if status_code == 200:
        logger.warning("response OK, status code 200!")
        logger.debug(health_response)
        sys.exit(0)
    
    status_code = 500 if status_code is None else status_code
    logger.error("response not in status code 200! Error exit...")
    logger.error(health_response)
    sys.exit(status_code)
