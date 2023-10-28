"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""


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
        return {
            "bbox": body["bbox"],
            "point": body["point"],
            "debug": debug
        }
    except KeyError as e_key_constants2:
        local_logger.error(f"e_key_constants2:{e_key_constants2}.")
        raise KeyError(f"e_key_constants2:{e_key_constants2}.")
    except Exception as e_constants2:
        local_logger.error(f"e_constants2:{e_constants2}.")
        raise e_constants2
