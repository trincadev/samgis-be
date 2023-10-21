"""helpers for compute measures: hash, time benchmarks"""
from pathlib import Path


def hash_calculate(arr: any, debug: bool = False) -> str or bytes:
    """
    Return computed hash from input variable (typically a numpy array).

    Args:
        arr: input variable
        debug: logging debug argument

    Returns:
        str or bytes: computed hash from input variable

    """
    import hashlib
    import numpy as np
    from base64 import b64encode

    from src.utilities.utilities import setup_logging
    local_logger = setup_logging(debug)

    if isinstance(arr, np.ndarray):
        hash_fn = hashlib.sha256(arr.data)
    elif isinstance(arr, dict):
        import json
        from src.utilities.serialize import serialize

        serialized = serialize(arr)
        variable_to_hash = json.dumps(serialized, sort_keys=True).encode('utf-8')
        hash_fn = hashlib.sha256(variable_to_hash)
    elif isinstance(arr, str):
        try:
            hash_fn = hashlib.sha256(arr)
        except TypeError:
            local_logger.warning(f"TypeError, re-try encoding arg:{arr},type:{type(arr)}.")
            hash_fn = hashlib.sha256(arr.encode('utf-8'))
    elif isinstance(arr, bytes):
        hash_fn = hashlib.sha256(arr)
    else:
        raise ValueError(f"variable 'arr':{arr} not yet handled.")
    return b64encode(hash_fn.digest())


def sha256sum(filename: Path or str) -> str:
    """
    Return computed hash for input file.

    Args:
        filename: input variable

    Returns:
        str: computed hash

    """
    import hashlib
    import mmap

    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
            h.update(mm)
    return h.hexdigest()


def perf_counter() -> float:
    """
    Performance counter for benchmarking.

    Returns:
        float: computed time value at execution time

    """
    import time
    return time.perf_counter()
