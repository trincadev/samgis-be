"""custom type hints"""
from enum import IntEnum, Enum
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


class PromptPointType(str, Enum):
    """Segment Anything: validation point prompt type"""
    point = "point"


class PromptRectangleType(str, Enum):
    """Segment Anything: validation rectangle prompt type"""
    rectangle = "rectangle"


class PromptLabel(IntEnum):
    """Valid prompt label type"""
    EXCLUDE = 0
    INCLUDE = 1


class ImagePixelCoordinates(TypedDict):
    """Image pixel coordinates type"""
    x: int
    y: int


class RawBBox(BaseModel):
    """Input lambda bbox request type (not yet parsed)"""
    ne: LatLngDict
    sw: LatLngDict


class RawPromptPoint(BaseModel):
    """Input lambda prompt request of type 'PromptPointType' - point (not yet parsed)"""
    type: PromptPointType
    data: LatLngDict
    label: PromptLabel


class RawPromptRectangle(BaseModel):
    """Input lambda prompt request of type 'PromptRectangleType' - rectangle (not yet parsed)"""
    type: PromptRectangleType
    data: RawBBox

    def get_type_str(self):
        return self.type

class RawRequestInput(BaseModel):
    """Input lambda request validator type (not yet parsed)"""
    bbox: RawBBox
    prompt: list[RawPromptPoint | RawPromptRectangle]
    zoom: int | float
    source_type: str = "Satellite"
    debug: bool = False
    url_tile: str = DEFAULT_TMS
