"""custom type hints"""
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


class RawBBox(BaseModel):
    ne: LatLngDict
    sw: LatLngDict


class RawPrompt(BaseModel):
    type: str
    data: LatLngDict
    label: int = 0


class RawRequestInput(BaseModel):
    bbox: RawBBox
    prompt: RawPrompt
    zoom: int | float
    source_type: str = "Satellite"


class ParsedPrompt(BaseModel):
    type: str
    data: llist_float
    label: int = 0


class ParsedRequestInput(BaseModel):
    bbox: llist_float
    prompt: ParsedPrompt
    zoom: int | float


class PixelCoordinate(TypedDict):
    x: int
    y: int
