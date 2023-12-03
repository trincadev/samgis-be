import os
from numpy import ndarray

from src import app_logger
from src.utilities.constants import (OUTPUT_CRS_STRING, DRIVER_RASTERIO_GTIFF, N_MAX_RETRIES, N_CONNECTION, N_WAIT,
                                     ZOOM_AUTO, BOOL_USE_CACHE)
from src.utilities.type_hints import tuple_ndarray_transform, tuple_float


bool_use_cache = int(os.getenv("BOOL_USE_CACHE", BOOL_USE_CACHE))
n_connection = int(os.getenv("N_CONNECTION", N_CONNECTION))
n_max_retries = int(os.getenv("N_MAX_RETRIES", N_MAX_RETRIES))
n_wait = int(os.getenv("N_WAIT", N_WAIT))
zoom_auto_string = os.getenv("ZOOM_AUTO", ZOOM_AUTO)


def download_extent(w: float, s: float, e: float, n: float, zoom: int or str = zoom_auto_string, source: str = None,
                    wait: int = n_wait, max_retries: int = n_max_retries, n_connections: int = n_connection,
                    use_cache: bool = bool_use_cache) -> tuple_ndarray_transform:
    """
    Download, merge and crop a list of tiles into a single geo-referenced image or a raster geodata

    Args:
        w: West edge
        s: South edge
        e: East edge
        n: North edge
        zoom: Level of detail
        source: xyzservices.TileProvider object or str
            [Optional. Default: OpenStreetMap Humanitarian web tiles]
            The tile source: web tile provider or path to local file. The web tile
            provider can be in the form of a :class:`xyzservices.TileProvider` object or a
            URL. The placeholders for the XYZ in the URL need to be `{x}`, `{y}`,
            `{z}`, respectively. For local file paths, the file is read with
            `rasterio` and all bands are loaded into the basemap.
            IMPORTANT: tiles are assumed to be in the Spherical Mercator
            projection (EPSG:3857), unless the `crs` keyword is specified.
        wait: if the tile API is rate-limited, the number of seconds to wait
            between a failed request and the next try
        max_retries: total number of rejected requests allowed before contextily will stop trying to fetch more tiles
            from a rate-limited API.
        n_connections: Number of connections for downloading tiles in parallel. Be careful not to overload the tile
            server and to check the tile provider's terms of use before increasing this value. E.g., OpenStreetMap has
            a max. value of 2 (https://operations.osmfoundation.org/policies/tiles/). If allowed to download in
            parallel, a recommended value for n_connections is 16, and should never be larger than 64.
        use_cache: If False, caching of the downloaded tiles will be disabled. This can be useful in resource
            constrained environments, especially when using n_connections > 1, or when a tile provider's terms of use
            don't allow caching.

    Returns:
        parsed request input
    """
    try:
        from src import contextily_tile
        from src.io.coordinates_pixel_conversion import _from4326_to3857

        app_logger.info(f"connection number:{n_connections}, type:{type(n_connections)}.")
        app_logger.info(f"zoom:{zoom}, type:{type(zoom)}.")
        app_logger.debug(f"download raster from source:{source} with bounding box w:{w}, s:{s}, e:{e}, n:{n}.")
        app_logger.debug(f"types w:{type(w)}, s:{type(s)}, e:{type(e)}, n:{type(n)}.")
        downloaded_raster, bbox_raster = contextily_tile.bounds2img(
            w, s, e, n, zoom=zoom, source=source, ll=True, wait=wait, max_retries=max_retries, n_connections=n_connections,
            use_cache=use_cache)
        xp0, yp0 = _from4326_to3857(n, e)
        xp1, yp1 = _from4326_to3857(s, w)
        cropped_image_ndarray, cropped_transform = crop_raster(yp1, xp1, yp0, xp0, downloaded_raster, bbox_raster)
        return cropped_image_ndarray, cropped_transform
    except Exception as e_download_extent:
        app_logger.exception(f"e_download_extent:{e_download_extent}.", exc_info=True)
        raise e_download_extent


def crop_raster(w: float, s: float, e: float, n: float, raster: ndarray, raster_bbox: tuple_float,
                crs: str = OUTPUT_CRS_STRING, driver: str = DRIVER_RASTERIO_GTIFF) -> tuple_ndarray_transform:
    """
    Crop a raster using given bounding box (w, s, e, n) values

    Args:
        w: cropping west edge
        s: cropping south edge
        e: cropping east edge
        n: cropping north edge
        raster: raster image to crop
        raster_bbox: bounding box of raster to crop
        crs: The coordinate reference system. Required in 'w' or 'w+' modes, it is ignored in 'r' or 'r+' modes.
        driver: A short format driver name (e.g. "GTiff" or "JPEG") or a list of such names (see GDAL docs at
            https://gdal.org/drivers/raster/index.html ). In 'w' or 'w+' modes a single name is required. In 'r' or 'r+'
            modes the driver can usually be omitted. Registered drivers will be tried sequentially until a match is
            found. When multiple drivers are available for a format such as JPEG2000, one of them can be selected by
            using this keyword argument.

    Returns:
        cropped raster with its Affine transform
    """
    try:
        from rasterio.io import MemoryFile
        from rasterio.mask import mask as rio_mask
        from shapely.geometry import Polygon
        from geopandas import GeoSeries

        app_logger.debug(f"raster: type {type(raster)}, raster_ext:{type(raster_bbox)}, {raster_bbox}.")
        img_to_save, transform = get_transform_raster(raster, raster_bbox)
        img_height, img_width, number_bands = img_to_save.shape
        # https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
        with MemoryFile() as rio_mem_file:
            app_logger.debug("writing raster in-memory to crop it with rasterio.mask.mask()")
            with rio_mem_file.open(
                    driver=driver,
                    height=img_height,
                    width=img_width,
                    count=number_bands,
                    dtype=str(img_to_save.dtype.name),
                    crs=crs,
                    transform=transform,
            ) as src_raster_rw:
                for band in range(number_bands):
                    src_raster_rw.write(img_to_save[:, :, band], band + 1)
            app_logger.debug("cropping raster in-memory with rasterio.mask.mask()")
            with rio_mem_file.open() as src_raster_ro:
                shapes_crop_polygon = Polygon([(n, e), (s, e), (s, w), (n, w), (n, e)])
                shapes_crop = GeoSeries([shapes_crop_polygon])
                app_logger.debug(f"cropping with polygon::{shapes_crop_polygon}.")
                cropped_image, cropped_transform = rio_mask(src_raster_ro, shapes=shapes_crop, crop=True)
                cropped_image_ndarray = reshape_as_image(cropped_image)
        app_logger.info(f"cropped image::{cropped_image_ndarray.shape}.")
        return cropped_image_ndarray, cropped_transform
    except Exception as e_crop_raster:
        app_logger.exception(f"arguments raster: {type(raster)}, {raster}.")
        app_logger.exception(f"e_crop_raster:{e_crop_raster}.", exc_info=True)
        raise e_crop_raster


def get_transform_raster(raster: ndarray, raster_bbox: tuple_float) -> tuple_ndarray_transform:
    """
    Convert the input raster image to RGB and extract the Affine 

    Args:
        raster: raster image to geo-reference
        raster_bbox: bounding box of raster to crop

    Returns:
        rgb raster image and its Affine transform
    """
    try:
        from rasterio.transform import from_origin
        from numpy import array as np_array, linspace as np_linspace, uint8 as np_uint8
        from PIL.Image import fromarray

        app_logger.debug(f"raster: type {type(raster)}, raster_ext:{type(raster_bbox)}, {raster_bbox}.")
        rgb = fromarray(np_uint8(raster)).convert('RGB')
        np_rgb = np_array(rgb)
        img_height, img_width, _ = np_rgb.shape

        min_x, max_x, min_y, max_y = raster_bbox
        app_logger.debug(f"raster rgb shape:{np_rgb.shape}, raster rgb bbox {raster_bbox}.")
        x = np_linspace(min_x, max_x, img_width)
        y = np_linspace(min_y, max_y, img_height)
        res_x = (x[-1] - x[0]) / img_width
        res_y = (y[-1] - y[0]) / img_height
        transform = from_origin(x[0] - res_x / 2, y[-1] + res_y / 2, res_x, res_y)
        return np_rgb, transform
    except Exception as e_get_transform_raster:
        app_logger.exception(f"arguments raster: {type(raster)}, {raster}.")
        app_logger.exception(f"arguments raster_bbox: {type(raster_bbox)}, {raster_bbox}.")
        app_logger.exception(f"e_get_transform_raster:{e_get_transform_raster}.")
        raise e_get_transform_raster


def reshape_as_image(arr):
    try:
        from numpy import swapaxes

        return swapaxes(swapaxes(arr, 0, 2), 0, 1)
    except Exception as e_reshape_as_image:
        app_logger.exception(f"arguments: {type(arr)}, {arr}.")
        app_logger.exception(f"e_reshape_as_image:{e_reshape_as_image}.", exc_info=True)
        raise e_reshape_as_image
