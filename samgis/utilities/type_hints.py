"""custom type hints"""
from enum import IntEnum, Enum, StrEnum
from typing import TypedDict

from PIL.Image import Image
from affine import Affine
from numpy import ndarray
from pydantic import BaseModel


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


class XYZDefaultProvidersNames(StrEnum):
    """Default xyz provider names"""
    DEFAULT_TILES_NAME_SHORT = "openstreetmap"
    DEFAULT_TILES_NAME = "openstreetmap.mapnik"


class XYZTerrainProvidersNames(StrEnum):
    """Custom xyz provider names for digital elevation models"""
    MAPBOX_TERRAIN_TILES_NAME = "mapbox.terrain-rgb"
    NEXTZEN_TERRAIN_TILES_NAME = "nextzen.terrarium"


class LatLngDict(BaseModel):
    """Generic geographic latitude-longitude type"""
    lat: float
    lng: float


class ContentTypes(str, Enum):
    """Segment Anything: validation point prompt type"""
    APPLICATION_JSON = "application/json"
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"


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


class ApiRequestBody(BaseModel):
    """Input lambda request validator type (not yet parsed)"""
    id: str = ""
    bbox: RawBBox
    prompt: list[RawPromptPoint | RawPromptRectangle]
    zoom: int | float
    source_type: str = "OpenStreetMap.Mapnik"
    debug: bool = False


class ApiResponseBodyFailure(BaseModel):
    duration_run: float
    message: str
    request_id: str


class ApiResponseBodySuccess(ApiResponseBodyFailure):
    n_predictions: int
    geojson: str
    n_shapes_geojson: int
