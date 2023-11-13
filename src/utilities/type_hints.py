"""custom type hints"""
from typing import List, Tuple
import numpy as np

ts_list_str1 = list[str]
ts_http2 = tuple[ts_list_str1, ts_list_str1]
ts_list_float2 = list[float, float]
ts_llist_float2 = list[ts_list_float2, ts_list_float2]
ts_geojson = dict[str, str, dict[str, dict[str]], list[str, dict[int], dict[str, list]]]
ts_float64_1 = tuple[np.float64, np.float64, np.float64, np.float64, np.float64, np.float64]
ts_float64_2 = tuple[np.float64, np.float64, np.float64, np.float64, np.float64, np.float64, np.float64]
ts_dict_str2 = dict[str, str]
ts_dict_str3 = dict[str, str, any]
ts_dict_str2b = dict[str, any]
ts_ddict1 = dict[str, dict[str, any], dict, dict, any]
ts_ddict2 = dict[str, dict, dict[str, list]]
ts_tuple_str2 = tuple[str, str]
ts_tuple_arr2 = tuple[np.ndarray, np.ndarray]
ts_tuple_flat2 = tuple[float, float]
ts_tuple_flat4 = tuple[float, float, float, float]
ts_list_float4 = list[float, float, float, float]
ts_tuple_int4 = tuple[int, int, int, int]
ts_llist2 = list[[int, int], [int, int]]
ts_ddict3 = dict[list[dict[float | int | str]], dict[float | int]]