"""custom type hints"""
from typing import TypedDict


ts_dict_str2 = dict[str, str]
ts_dict_str3 = dict[str, str, any]
ts_ddict1 = dict[str, dict[str, any], dict, dict, any]
# ts_list_float = list[float, float]


class PixelCoordinate(TypedDict):
    x: int
    y: int
