"""
Download geo-referenced raster tiles images.
Modified from https://github.com/gumblex/tms2geotiff/

BSD 2-Clause License

Copyright (c) 2019, Dingyuan Wang
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import concurrent.futures
import io
import itertools
import math
import re
import time
from typing import Tuple, Callable
import PIL
from PIL import Image

from src import app_logger
from src.utilities.constants import EARTH_EQUATORIAL_RADIUS, RETRY_DOWNLOAD, TIMEOUT_DOWNLOAD, TILE_SIZE, \
    CALLBACK_INTERVAL_DOWNLOAD
from src.utilities.type_hints import PIL_Image

Image.MAX_IMAGE_PIXELS = None

try:
    import httpx

    SESSION = httpx.Client()
except ImportError:
    import requests

    SESSION = requests.Session()

SESSION.headers.update({
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
})

re_coords_split = re.compile('[ ,;]+')


def from4326_to3857(lat, lon):
    x_tile = math.radians(lon) * EARTH_EQUATORIAL_RADIUS
    y_tile = math.log(math.tan(math.radians(45 + lat / 2.0))) * EARTH_EQUATORIAL_RADIUS
    return x_tile, y_tile


def deg2num(lat, lon, zoom):
    n = 2 ** zoom
    x_tile = ((lon + 180) / 360 * n)
    y_tile = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) * n / 2
    return x_tile, y_tile


def is_empty(im):
    extrema = im.getextrema()
    if len(extrema) >= 3:
        if len(extrema) > 3 and extrema[-1] == (0, 0):
            return True
        for ext in extrema[:3]:
            if ext != (0, 0):
                return False
        return True
    else:
        return extrema[0] == (0, 0)


def paste_tile(big_im, base_size, tile, corner_xy, bbox):
    if tile is None:
        return big_im
    im = Image.open(io.BytesIO(tile))
    mode = 'RGB' if im.mode == 'RGB' else 'RGBA'
    size = im.size
    if big_im is None:
        base_size[0] = size[0]
        base_size[1] = size[1]
        new_im = Image.new(mode, (
            size[0] * (bbox[2] - bbox[0]), size[1] * (bbox[3] - bbox[1])))
    else:
        new_im = big_im

    dx = abs(corner_xy[0] - bbox[0])
    dy = abs(corner_xy[1] - bbox[1])
    xy0 = (size[0] * dx, size[1] * dy)
    if mode == 'RGB':
        new_im.paste(im, xy0)
    else:
        if im.mode != mode:
            im = im.convert(mode)
        if not is_empty(im):
            new_im.paste(im, xy0)
    im.close()
    return new_im


def get_tile(url):
    retry = RETRY_DOWNLOAD
    while 1:
        try:
            app_logger.debug(f"image tile url to download: {url}.")
            r = SESSION.get(url, timeout=TIMEOUT_DOWNLOAD)
            break
        except Exception as request_tile_exception:
            app_logger.error(f"retry {retry}, request_tile_exception:{request_tile_exception}.")
            retry -= 1
            if not retry:
                raise
    if r.status_code == 404 or not r.content:
        return None
    r.raise_for_status()
    return r.content


def print_progress(progress, total, done=False):
    if done:
        app_logger.info('Downloaded image %d/%d, %.2f%%' % (progress, total, progress * 100 / total))


def download_extent(
        source: str, lat0: float, lon0: float, lat1: float, lon1: float, zoom: int,
        save_image: bool = True, progress_callback: Callable = print_progress,
        callback_interval: float = CALLBACK_INTERVAL_DOWNLOAD
) -> Tuple[PIL_Image, Tuple[float]] or Tuple[None]:
    """
    Download, merge and crop a list of tiles into a single geo-referenced image or a raster geodata

    Args:
        source: remote url tile
        lat0: point0 bounding box latitude
        lat1: point0 bounding box longitude
        lon0: point1 bounding box latitude
        lon1: point1 bounding box longitude
        zoom: bounding box zoom
        save_image: boolean to choose if save the image
        progress_callback: callback function
        callback_interval: process callback interval time

    Returns:
        parsed request input
    """
    x0, y0 = deg2num(lat0, lon0, zoom)
    x1, y1 = deg2num(lat1, lon1, zoom)
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0

    corners = tuple(itertools.product(
        range(math.floor(x0), math.ceil(x1)),
        range(math.floor(y0), math.ceil(y1))))
    total_num = len(corners)
    futures = {}
    done_num = 0
    progress_callback(done_num, total_num, False)
    last_done_num = 0
    last_callback = time.monotonic()
    cancelled = False
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        for x, y in corners:
            future = executor.submit(get_tile, source.format(z=zoom, x=x, y=y))
            futures[future] = (x, y)
        bbox = (math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1))
        big_im = None
        base_size = [TILE_SIZE, TILE_SIZE]
        big_im, cancelled, done_num = run_future_tile_download(
            base_size, bbox, big_im, callback_interval, cancelled, done_num, futures, last_callback, last_done_num,
            progress_callback, save_image, total_num
        )
    if cancelled:
        raise TaskCancelled()
    progress_callback(done_num, total_num, True)

    if not save_image:
        return None, None

    x_frac = x0 - bbox[0]
    y_frac = y0 - bbox[1]
    x2 = round(base_size[0] * x_frac)
    y2 = round(base_size[1] * y_frac)
    img_w = round(base_size[0] * (x1 - x0))
    img_h = round(base_size[1] * (y1 - y0))
    final_image = big_im.crop((x2, y2, x2 + img_w, y2 + img_h))
    if final_image.mode == 'RGBA' and final_image.getextrema()[3] == (255, 255):
        final_image = final_image.convert('RGB')
    big_im.close()
    xp0, yp0 = from4326_to3857(lat0, lon0)
    xp1, yp1 = from4326_to3857(lat1, lon1)
    p_width = abs(xp1 - xp0) / final_image.size[0]
    p_height = abs(yp1 - yp0) / final_image.size[1]
    matrix = min(xp0, xp1), p_width, 0, max(yp0, yp1), 0, -p_height
    return final_image, matrix


def run_future_tile_download(
        base_size, bbox, big_im, callback_interval, cancelled, done_num, futures, last_callback, last_done_num,
        progress_callback, save_image, total_num
):
    while futures:
        done, _ = concurrent.futures.wait(
            futures.keys(), timeout=callback_interval,
            return_when=concurrent.futures.FIRST_COMPLETED
        )
        for fut in done:
            img_data = fut.result()
            xy = futures[fut]
            if save_image:
                big_im = paste_tile(big_im, base_size, img_data, xy, bbox)
            del futures[fut]
            done_num += 1
        if time.monotonic() > last_callback + callback_interval:
            try:
                progress_callback(done_num, total_num, (done_num > last_done_num))
            except TaskCancelled:
                for fut in futures.keys():
                    fut.cancel()
                futures.clear()
                cancelled = True
                break
            last_callback = time.monotonic()
            last_done_num = done_num
    return big_im, cancelled, done_num


class TaskCancelled(RuntimeError):
    pass
