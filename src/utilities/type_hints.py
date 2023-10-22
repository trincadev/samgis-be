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
