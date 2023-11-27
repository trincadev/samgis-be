"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""
from src import app_logger
from src.utilities.serialize import serialize


def _prepare_base64_input(sb):
    if isinstance(sb, str):
        # If there's any unicode here, an exception will be thrown and the function will return false
        return bytes(sb, 'ascii')
    elif isinstance(sb, bytes):
        return sb
    raise ValueError("Argument must be string or bytes")


def _is_base64(sb: str or bytes):
    import base64

    try:
        sb_bytes = _prepare_base64_input(sb)
        return base64.b64encode(base64.b64decode(sb_bytes, validate=True)) == sb_bytes
    except ValueError:
        return False


def base64_decode(s):
    """
    Decode base64 strings

    Args:
        s: input string

    Returns:
        decoded string
    """
    import base64

    if isinstance(s, str) and _is_base64(s):
        return base64.b64decode(s, validate=True).decode("utf-8")

    return s


def base64_encode(sb: str or bytes) -> bytes:
    """
    Encode input strings or bytes as base64

    Args:
        sb: input string or bytes

    Returns:
        base64 encoded bytes
    """
    import base64

    sb_bytes = _prepare_base64_input(sb)
    return base64.b64encode(sb_bytes)


def hash_calculate(arr) -> str or bytes:
    """
    Return computed hash from input variable (typically a numpy array).

    Args:
        arr: input variable

    Returns:
        computed hash from input variable
    """
    import hashlib
    import numpy as np
    from base64 import b64encode

    if isinstance(arr, np.ndarray):
        hash_fn = hashlib.sha256(arr.data)
    elif isinstance(arr, dict):
        import json

        serialized = serialize(arr)
        variable_to_hash = json.dumps(serialized, sort_keys=True).encode('utf-8')
        hash_fn = hashlib.sha256(variable_to_hash)
    elif isinstance(arr, str):
        try:
            hash_fn = hashlib.sha256(arr)
        except TypeError:
            app_logger.warning(f"TypeError, re-try encoding arg:{arr},type:{type(arr)}.")
            hash_fn = hashlib.sha256(arr.encode('utf-8'))
    elif isinstance(arr, bytes):
        hash_fn = hashlib.sha256(arr)
    else:
        raise ValueError(f"variable 'arr':{arr} not yet handled.")
    return b64encode(hash_fn.digest())
