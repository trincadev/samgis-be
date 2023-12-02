"""custom type hints"""
from enum import Enum
from typing import TypedDict

from PIL.Image import Image
from affine import Affine
from numpy import ndarray
from pydantic import BaseModel

from src.utilities.constants import DEFAULT_TMS


dict_str_int = dict[str, int]
dict_str = dict[str]
dict_str_any = dict[str, any]
list_dict = list[dict]
list_float = list[float]
list_int = list[int]
tuple_int = tuple[int]
tuple_ndarr_int = tuple[ndarray, int]
llist_float = list[list_float]
tuple_float = tuple[float]
tuple_float_any = tuple[float, any]
PIL_Image = Image
tuple_ndarray_transform = tuple[ndarray, Affine]


class LatLngDict(BaseModel):
    """Generic geographic latitude-longitude type"""
    lat: float
    lng: float


class PromptType(str, Enum):
    """Segment Anything enumeration prompt type"""
    # rectangle = "rectangle"
    point = "point"


class ImagePixelCoordinates(TypedDict):
    """Image pixel coordinates type"""
    x: int
    y: int


class RawBBox(BaseModel):
    """Input lambda bbox request type (not parsed)"""
    ne: LatLngDict
    sw: LatLngDict


class RawPrompt(BaseModel):
    """Input lambda prompt request type (not parsed)"""
    type: PromptType
    data: LatLngDict
    label: int = 0


class RawRequestInput(BaseModel):
    """Input lambda request validator type (not parsed)"""
    bbox: RawBBox
    prompt: list[RawPrompt]
    zoom: int | float
    source_type: str = "Satellite"
    debug: bool = False
    url_tile: str = DEFAULT_TMS
