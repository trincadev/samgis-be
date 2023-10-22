"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""
import loguru

from src.utilities.constants import ROOT


def setup_logging(debug: bool = False, formatter: str = "{time} - {level} - ({extra[request_id]}) {message} ") -> loguru.logger:
    """
    Create a logging instance with log string formatter.

    Args:
        debug: logging debug argument
        formatter: log string formatter

    Returns:
        Logger

    """
    import sys

    logger = loguru.logger
    logger.remove()
    level_logger = "DEBUG" if debug else "INFO"
    logger.add(sys.stdout, format=formatter, level=level_logger)
    logger.debug(f"type_logger:{type(logger)}.")
    return logger


def get_constants(event: dict, root: str = ROOT, dotenv_filename: str = ".env", debug=False) -> dict:
    """
    Return constants we need to use from event, context and environment variables (both production and test).
    
    Args:
        event: request event
        root: path containing the dotenv file
        dotenv_filename: dotenv filename
        debug: logging debug argument

    Returns:
        dict: project constants object

    """
    import json
    import os
    # from dotenv import dotenv_values

    from src.utilities.constants import SKIP_CONDITIONS_LIST
    local_logger = setup_logging(debug)
    try:
        body = event["body"]
    except Exception as e_constants1:
        local_logger.error(f"e_constants1:{e_constants1}.")
        body = event

    if isinstance(body, str):
        body = json.loads(event["body"])

    try:
        debug = body["debug"]
        local_logger.info(f"re-try get debug value:{debug}, log_level:{local_logger.level}.")
        local_logger = setup_logging(debug)
    except KeyError:
        local_logger.error("get_constants:: no debug key, pass...")
    local_logger.debug(f"constants debug:{debug}, log_level:{local_logger.level}, body:{body}.")

    try:
        dotenv_file_path = os.path.join(root, dotenv_filename)
        local_logger.info(f"root_path:{root}, dotenv file:{dotenv_file_path}.")
        # secrets = dotenv_values(dotenv_file_path)

        try:
            skip_conditions_list = body["skip_conditions_list"]
            local_logger.info(f"found skip_conditions_list, using it: {skip_conditions_list}.")
        except KeyError:
            skip_conditions_list = SKIP_CONDITIONS_LIST

        return {
            "bounding_box": body["bounding_box"],
            "zoom": body["zoom"],
            "debug": debug,
            "slope_cellsize": body["slope_cellsize"],
            "model_project_name": body["model_project_name"],
            "model_version": body["model_version"],
            "skip_conditions_list": skip_conditions_list
        }
    except KeyError as e_key_constants2:
        local_logger.error(f"e_key_constants2:{e_key_constants2}.")
        raise KeyError(f"e_key_constants2:{e_key_constants2}.")
    except Exception as e_constants2:
        local_logger.error(f"e_constants2:{e_constants2}.")
        raise e_constants2
