"""custom type hints"""
from typing import List, Tuple

input_floatlist = List[float]
input_floatlist2 = List[input_floatlist]
input_float_tuples = List[Tuple[float, float]]
ts_dict_str2 = dict[str, str]
ts_dict_str3 = dict[str, str, any]
