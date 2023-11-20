"""custom type hints"""
from enum import Enum

from pydantic import BaseModel
from typing import TypedDict


ts_dict_str2 = dict[str, str]
ts_dict_str3 = dict[str, str, any]
ts_ddict1 = dict[str, dict[str, any], dict, dict, any]
list_float = list[float]
llist_float = list[list_float]


class LatLngDict(BaseModel):
    lat: float
    lng: float


class PromptType(str, Enum):
    point = "point"
    # rectangle = "rectangle"


class ParsedPrompt(BaseModel):
    type: PromptType
    data: llist_float
    label: int = 0


class ParsedRequestInput(BaseModel):
    bbox: llist_float
    prompt: ParsedPrompt
    zoom: int | float


class PixelCoordinate(TypedDict):
    x: int
    y: int


class RawBBox(BaseModel):
    ne: LatLngDict
    sw: LatLngDict


class RawPrompt(BaseModel):
    type: PromptType
    data: LatLngDict
    label: int = 0


class RawRequestInput(BaseModel):
    bbox: RawBBox
    prompt: list[RawPrompt]
    zoom: int | float
    source_type: str = "Satellite"
    debug: bool = False
