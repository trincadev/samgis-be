"""custom type hints"""
from enum import Enum

from pydantic import BaseModel
from typing import TypedDict

from src.utilities.constants import DEFAULT_TMS

ts_dict_str2 = dict[str, str]
ts_dict_str3 = dict[str, str, any]
ts_ddict1 = dict[str, dict[str, any], dict, dict, any]
list_float = list[float]
llist_float = list[list_float]


class LatLngDict(BaseModel):
    """A latitude-longitude type"""
    lat: float
    lng: float


class PromptType(str, Enum):
    """Segment Anything enumeration prompt type"""
    point = "point"
    # rectangle = "rectangle"


class ImagePixelCoordinates(TypedDict):
    x: int
    y: int


class RawBBox(BaseModel):
    """Input lambda bbox request - not parsed"""
    ne: LatLngDict
    sw: LatLngDict


class RawPrompt(BaseModel):
    """Input lambda prompt request - not parsed"""
    type: PromptType
    data: LatLngDict
    label: int = 0


class RawRequestInput(BaseModel):
    """Input lambda request - not parsed"""
    bbox: RawBBox
    prompt: list[RawPrompt]
    zoom: int | float
    source_type: str = "Satellite"
    debug: bool = False
    url_tile: str = DEFAULT_TMS
