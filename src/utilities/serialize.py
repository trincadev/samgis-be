"""Serialize objects"""
from typing import Mapping

from src import app_logger
from src.utilities.type_hints import ts_dict_str2, ts_dict_str3


def serialize(obj: any, include_none: bool = False) -> object:
    """
    Return the input object into a serializable one

    Args:
        obj: Object to serialize
        include_none: bool to indicate if include also keys with None values during dict serialization

    Returns:
        object: serialized object

    """
    return _serialize(obj, include_none)


def _serialize(obj: any, include_none: bool) -> any:
    import numpy as np

    primitive = (int, float, str, bool)
    # print(type(obj))
    try:
        if obj is None:
            return None
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, primitive):
            return obj
        elif type(obj) is list:
            return _serialize_list(obj, include_none)
        elif type(obj) is tuple:
            return list(obj)
        elif type(obj) is bytes:
            return _serialize_bytes(obj)
        elif isinstance(obj, Exception):
            return _serialize_exception(obj)
        # elif isinstance(obj, object):
        #     return _serialize_object(obj, include_none)
        else:
            return _serialize_object(obj, include_none)
    except Exception as e_serialize:
        app_logger.error(f"e_serialize::{e_serialize}, type_obj:{type(obj)}, obj:{obj}.")
        return f"object_name:{str(obj)}__object_type_str:{str(type(obj))}."


def _serialize_object(obj: Mapping[any, object], include_none: bool) -> dict[any]:
    from bson import ObjectId

    res = {}
    if type(obj) is not dict:
        keys = [i for i in obj.__dict__.keys() if (getattr(obj, i) is not None) or include_none]
    else:
        keys = [i for i in obj.keys() if (obj[i] is not None) or include_none]
    for key in keys:
        if type(obj) is not dict:
            res[key] = _serialize(getattr(obj, key), include_none)
        elif isinstance(obj[key], ObjectId):
            continue
        else:
            res[key] = _serialize(obj[key], include_none)
    return res


def _serialize_list(ls: list, include_none: bool) -> list:
    return [_serialize(elem, include_none) for elem in ls]


def _serialize_bytes(b: bytes) -> ts_dict_str2:
    import base64
    encoded = base64.b64encode(b)
    return {"value": encoded.decode('ascii'), "type": "bytes"}


def _serialize_exception(e: Exception) -> ts_dict_str3:
    return {"msg": str(e), "type": str(type(e)), **e.__dict__}
