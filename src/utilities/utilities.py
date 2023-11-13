"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""
import numpy as np

from src import app_logger
from src.utilities.type_hints import ts_float64_1, ts_float64_2


def is_base64(sb):
    import base64

    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes, validate=True)) == sb_bytes
    except ValueError:
        return False


def get_system_info():
    import multiprocessing
    import torch.multiprocessing as mp
    import os
    import subprocess

    app_logger.info(f"mp::cpu_count:{mp.cpu_count()}.")
    app_logger.info(f"multiprocessing::cpu_count:{multiprocessing.cpu_count()}.")
    app_logger.info(f"os::cpu_count:{os.cpu_count()}")
    app_logger.info(f"os::sched_getaffinity:{len(os.sched_getaffinity(0))}")
    lscpu_output = subprocess.run("/usr/bin/lscpu", capture_output=True)
    app_logger.info(f"lscpu:{lscpu_output.stdout.decode('utf-8')}.")
    free_mem_output = subprocess.run(["/usr/bin/free", "-m"], capture_output=True)
    app_logger.info(f"free_mem_output:{free_mem_output.stdout.decode('utf-8')}.")


def base64_decode(s):
    import base64

    if isinstance(s, str) and is_base64(s):
        return base64.b64decode(s, validate=True).decode("utf-8")

    return s


def get_constants(event: dict, debug=False) -> dict:
    """
    Return constants we need to use from event, context and environment variables (both production and test).

    Args:
        event: request event
        debug: logging debug argument

    Returns:
        dict: project constants object

    """
    import json

    try:
        body = event["body"]
    except Exception as e_constants1:
        app_logger.error(f"e_constants1:{e_constants1}.")
        body = event

    if isinstance(body, str):
        body = json.loads(event["body"])

    try:
        debug = body["debug"]
        app_logger.info(f"re-try get debug value:{debug}, log_level:{app_logger.level}.")
    except KeyError:
        app_logger.error("get_constants:: no debug key, pass...")
    app_logger.info(f"constants debug:{debug}, log_level:{app_logger.level}, body:{body}.")

    try:
        return {
            "bbox": body["bbox"],
            "point": body["point"],
            "debug": debug
        }
    except KeyError as e_key_constants2:
        app_logger.error(f"e_key_constants2:{e_key_constants2}.")
        raise KeyError(f"e_key_constants2:{e_key_constants2}.")
    except Exception as e_constants2:
        app_logger.error(f"e_constants2:{e_constants2}.")
        raise e_constants2


def get_rasters_info(rasters_list:list, names_list:list, title:str="", debug:bool=False) -> str:
    """
    Analyze numpy arrays' list to extract a string containing some useful information. For every raster:

        - type of raster
        - raster.dtype if that's instance of np.ndarray
        - raster shape
        - min of raster value, over all axis (flattening the array)
        - max of raster value, over all axis (flattening the array)
        - mean of raster value, over all axis (flattening the array)
        - median of raster value, over all axis (flattening the array)
        - standard deviation of raster value, over all axis (flattening the array)
        - variance of raster value, over all axis (flattening the array)

    Raises:
        ValueError if raster_list and names_list have a different number of elements

    Args:
        rasters_list: list of numpy array raster to analyze
        names_list: string list of numpy array
        title: title of current analytic session
        debug: logging debug argument

    Returns:
        str: the collected information

    """

    msg = f"get_rasters_info::title:{title},\n"
    if not len(rasters_list) == len(names_list):
        msg = "raster_list and names_list should have the same number of elements:\n"
        msg += f"len(rasters_list):{len(rasters_list)}, len(names_list):{len(names_list)}."
        raise ValueError(msg)
    try:
        for raster, name in zip(rasters_list, names_list):
            try:
                if isinstance(raster, np.ndarray):
                    shape_or_len = raster.shape
                elif isinstance(raster, list):
                    shape_or_len = len(raster)
                else:
                    raise ValueError(f"wrong argument type:{raster}, variable:{raster}.")
                zmin, zmax, zmean, zmedian, zstd, zvar = get_stats_raster(raster, debug=debug)
                msg += "name:{}:type:{},dtype:{},shape:{},min:{},max:{},mean:{},median:{},std:{},var:{}\n".format(
                    name, type(raster), raster.dtype if isinstance(raster, np.ndarray) else None, shape_or_len, zmin,
                    zmax, zmean, zmedian, zstd, zvar
                )
            except Exception as get_rasters_types_e:
                msg = f"get_rasters_types_e::{get_rasters_types_e}, type_raster:{type(raster)}."
                app_logger.error(msg)
                raise ValueError(msg)
    except IndexError as get_rasters_types_ie:
        app_logger.error(f"get_rasters_types::len:rasters_list:{len(rasters_list)}, len_names_list:{len(names_list)}.")
        raise get_rasters_types_ie
    return msg + "\n=============================\n"


def get_stats_raster(raster: np.ndarray, get_rms:bool=False, debug:bool=False) -> ts_float64_1 or ts_float64_2:
    """
    Analyze a numpy arrays to extract a tuple of useful information:

        - type of raster
        - raster.dtype if that's instance of np.ndarray
        - raster shape
        - min of raster value, over all axis (flattening the array)
        - max of raster value, over all axis (flattening the array)
        - mean of raster value, over all axis (flattening the array)
        - median of raster value, over all axis (flattening the array)
        - standard deviation of raster value, over all axis (flattening the array)
        - variance of raster value, over all axis (flattening the array)

    Args:
        raster: numpy array to analyze
        get_rms: bool to get Root Mean Square Error
        debug: logging debug argument

    Returns:
        tuple: float values (min, max, mean, median, standard deviation, variance of raster)

    """
    std = np.nanstd(raster)
    if get_rms:
        try:
            rms = np.sqrt(np.nanmean(np.square(raster)))
        except Exception as rms_e:
            rms = None
            app_logger.error(f"get_stats_raster::rms_Exception:{rms_e}.")
        app_logger.info(f"nanmin:{type(np.nanmin(raster))}.")
        return (np.nanmin(raster), np.nanmax(raster), np.nanmean(raster), np.nanmedian(raster), std,
                np.nanvar(raster), rms)
    return (np.nanmin(raster), np.nanmax(raster), np.nanmean(raster), np.nanmedian(raster), np.nanstd(raster),
            np.nanvar(raster))
