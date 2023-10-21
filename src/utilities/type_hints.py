"""custom type hints"""
from typing import List, Dict, Tuple

import numpy as np

# ts_ddict1, ts_float64_1, ts_float64_2, ts_dict_str3, ts_dict_str2
input_floatlist = List[float]
input_floatlist2 = List[input_floatlist]
ts_ddict1 = Dict[str, Dict[str, any], Dict, Dict, any]
ts_dict_str2 = Dict[str, str]
ts_dict_str3 = Dict[str, str, any]
ts_float64_1 = Tuple[np.float64, np.float64, np.float64, np.float64, np.float64, np.float64]
ts_float64_2 = Tuple[np.float64, np.float64, np.float64, np.float64, np.float64, np.float64, np.float64]

"""
ts_list_str1 = List[str]
ts_http2 = Tuple[ts_list_str1, ts_list_str1]
ts_list_float2 = List[float, float]
ts_llist_float2 = List[ts_list_float2, ts_list_float2]
ts_geojson = Dict[str, str, Dict[str, Dict[str]], List[str, Dict[int], Dict[str, List]]]
ts_dict_str2b = Dict[str, any]
ts_ddict2 = Dict[str, Dict, Dict[str, List]]
ts_tuple_str2 = Tuple[str, str]
ts_tuple_arr2 = Tuple[np.ndarray, np.ndarray]
ts_tuple_flat2 = Tuple[float, float]
ts_tuple_flat4 = Tuple[float, float, float, float]
ts_list_float4 = List[float, float, float, float]
ts_tuple_int4 = Tuple[int, int, int, int]
ts_ddict3 = Dict[List[Dict[float | int | str]], Dict[float | int]]
"""