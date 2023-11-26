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
import sqlite3
import time

from PIL import Image

from src import app_logger
from src.utilities.constants import EARTH_EQUATORIAL_RADIUS


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
    xtile = math.radians(lon) * EARTH_EQUATORIAL_RADIUS
    ytile = math.log(math.tan(math.radians(45 + lat / 2.0))) * EARTH_EQUATORIAL_RADIUS
    return xtile, ytile


def deg2num(lat, lon, zoom):
    n = 2 ** zoom
    xtile = ((lon + 180) / 360 * n)
    ytile = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) * n / 2
    return xtile, ytile


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


def mbtiles_init(dbname):
    db = sqlite3.connect(dbname, isolation_level=None)
    cur = db.cursor()
    cur.execute("BEGIN")
    cur.execute("CREATE TABLE IF NOT EXISTS metadata (name TEXT PRIMARY KEY, value TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS tiles ("
                "zoom_level INTEGER NOT NULL, "
                "tile_column INTEGER NOT NULL, "
                "tile_row INTEGER NOT NULL, "
                "tile_data BLOB NOT NULL, "
                "UNIQUE (zoom_level, tile_column, tile_row)"
                ")")
    cur.execute("COMMIT")
    return db


def paste_tile(bigim, base_size, tile, corner_xy, bbox):
    if tile is None:
        return bigim
    im = Image.open(io.BytesIO(tile))
    mode = 'RGB' if im.mode == 'RGB' else 'RGBA'
    size = im.size
    if bigim is None:
        base_size[0] = size[0]
        base_size[1] = size[1]
        newim = Image.new(mode, (
            size[0] * (bbox[2] - bbox[0]), size[1] * (bbox[3] - bbox[1])))
    else:
        newim = bigim

    dx = abs(corner_xy[0] - bbox[0])
    dy = abs(corner_xy[1] - bbox[1])
    xy0 = (size[0] * dx, size[1] * dy)
    if mode == 'RGB':
        newim.paste(im, xy0)
    else:
        if im.mode != mode:
            im = im.convert(mode)
        if not is_empty(im):
            newim.paste(im, xy0)
    im.close()
    return newim


def get_tile(url):
    retry = 3
    while 1:
        try:
            app_logger.info(f"image tile url to download: {url}.")
            r = SESSION.get(url, timeout=60)
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


def mbtiles_save(db, img_data, xy, zoom, img_format):
    if not img_data:
        return
    im = Image.open(io.BytesIO(img_data))
    if im.format == 'PNG':
        current_format = 'png'
    elif im.format == 'JPEG':
        current_format = 'jpg'
    elif im.format == 'WEBP':
        current_format = 'webp'
    else:
        current_format = 'image/' + im.format.lower()
    x, y = xy
    y = 2 ** zoom - 1 - y
    cur = db.cursor()
    if img_format is None or img_format == current_format:
        cur.execute("REPLACE INTO tiles VALUES (?,?,?,?)", (
            zoom, x, y, img_data))
        return img_format or current_format
    buf = io.BytesIO()
    if img_format == 'png':
        im.save(buf, 'PNG')
    elif img_format == 'jpg':
        im.save(buf, 'JPEG', quality=93)
    elif img_format == 'webp':
        im.save(buf, 'WEBP')
    else:
        im.save(buf, img_format.split('/')[-1].upper())
    cur.execute("REPLACE INTO tiles VALUES (?,?,?,?)", (
        zoom, x, y, buf.getvalue()))
    return img_format


def download_extent(
        source, lat0, lon0, lat1, lon1, zoom,
        mbtiles=None, save_image=True,
        progress_callback=print_progress,
        callback_interval=0.05
):
    x0, y0 = deg2num(lat0, lon0, zoom)
    x1, y1 = deg2num(lat1, lon1, zoom)
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0

    db = None
    mbt_img_format = None
    if mbtiles:
        db = mbtiles_init(mbtiles)
        cur = db.cursor()
        cur.execute("BEGIN")
        cur.execute("REPLACE INTO metadata VALUES ('name', ?)", (source,))
        cur.execute("REPLACE INTO metadata VALUES ('type', 'overlay')")
        cur.execute("REPLACE INTO metadata VALUES ('version', '1.1')")
        cur.execute("REPLACE INTO metadata VALUES ('description', ?)", (source,))
        cur.execute("SELECT value FROM metadata WHERE name='format'")
        row = cur.fetchone()
        if row and row[0]:
            mbt_img_format = row[0]
        else:
            cur.execute("REPLACE INTO metadata VALUES ('format', 'png')")

        lat_min = min(lat0, lat1)
        lat_max = max(lat0, lat1)
        lon_min = min(lon0, lon1)
        lon_max = max(lon0, lon1)
        bounds = [lon_min, lat_min, lon_max, lat_max]
        cur.execute("SELECT value FROM metadata WHERE name='bounds'")
        row = cur.fetchone()
        if row and row[0]:
            last_bounds = [float(x) for x in row[0].split(',')]
            bounds[0] = min(last_bounds[0], bounds[0])
            bounds[1] = min(last_bounds[1], bounds[1])
            bounds[2] = max(last_bounds[2], bounds[2])
            bounds[3] = max(last_bounds[3], bounds[3])
        cur.execute("REPLACE INTO metadata VALUES ('bounds', ?)", (
            ",".join(map(str, bounds)),))
        cur.execute("REPLACE INTO metadata VALUES ('center', ?)", ("%s,%s,%d" % (
            (lon_max + lon_min) / 2, (lat_max + lat_min) / 2, zoom),))
        cur.execute("""
            INSERT INTO metadata VALUES ('minzoom', ?)
            ON CONFLICT(name) DO UPDATE SET value=excluded.value
            WHERE CAST(excluded.value AS INTEGER)<CAST(metadata.value AS INTEGER)
        """, (str(zoom),))
        cur.execute("""
            INSERT INTO metadata VALUES ('maxzoom', ?)
            ON CONFLICT(name) DO UPDATE SET value=excluded.value
            WHERE CAST(excluded.value AS INTEGER)>CAST(metadata.value AS INTEGER)
        """, (str(zoom),))
        cur.execute("COMMIT")

    corners = tuple(itertools.product(
        range(math.floor(x0), math.ceil(x1)),
        range(math.floor(y0), math.ceil(y1))))
    totalnum = len(corners)
    futures = {}
    done_num = 0
    progress_callback(done_num, totalnum, False)
    last_done_num = 0
    last_callback = time.monotonic()
    cancelled = False
    with concurrent.futures.ThreadPoolExecutor(5) as executor:
        for x, y in corners:
            future = executor.submit(get_tile, source.format(z=zoom, x=x, y=y))
            futures[future] = (x, y)
        bbox = (math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1))
        bigim = None
        base_size = [256, 256]
        while futures:
            done, _ = concurrent.futures.wait(
                futures.keys(), timeout=callback_interval,
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            cur = None
            if mbtiles:
                cur = db.cursor()
                cur.execute("BEGIN")
            for fut in done:
                img_data = fut.result()
                xy = futures[fut]
                if save_image:
                    bigim = paste_tile(bigim, base_size, img_data, xy, bbox)
                if mbtiles:
                    new_format = mbtiles_save(db, img_data, xy, zoom, mbt_img_format)
                    if not mbt_img_format:
                        cur.execute(
                            "UPDATE metadata SET value=? WHERE name='format'",
                            (new_format,))
                        mbt_img_format = new_format
                del futures[fut]
                done_num += 1
            if mbtiles:
                cur.execute("COMMIT")
            if time.monotonic() > last_callback + callback_interval:
                try:
                    progress_callback(done_num, totalnum, (done_num > last_done_num))
                except TaskCancelled:
                    for fut in futures.keys():
                        fut.cancel()
                    futures.clear()
                    cancelled = True
                    break
                last_callback = time.monotonic()
                last_done_num = done_num
    if cancelled:
        raise TaskCancelled()
    progress_callback(done_num, totalnum, True)

    if not save_image:
        return None, None

    xfrac = x0 - bbox[0]
    yfrac = y0 - bbox[1]
    x2 = round(base_size[0] * xfrac)
    y2 = round(base_size[1] * yfrac)
    imgw = round(base_size[0] * (x1 - x0))
    imgh = round(base_size[1] * (y1 - y0))
    retim = bigim.crop((x2, y2, x2 + imgw, y2 + imgh))
    if retim.mode == 'RGBA' and retim.getextrema()[3] == (255, 255):
        retim = retim.convert('RGB')
    bigim.close()
    xp0, yp0 = from4326_to3857(lat0, lon0)
    xp1, yp1 = from4326_to3857(lat1, lon1)
    pwidth = abs(xp1 - xp0) / retim.size[0]
    pheight = abs(yp1 - yp0) / retim.size[1]
    matrix = (min(xp0, xp1), pwidth, 0, max(yp0, yp1), 0, -pheight)
    return retim, matrix


class TaskCancelled(RuntimeError):
    pass
