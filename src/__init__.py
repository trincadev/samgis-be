"""Get machine learning predictions from geodata raster images"""
from aws_lambda_powertools import Logger
# not used here but contextily_tile is imported in src.io.tms2geotiff
from contextily import tile as contextily_tile
from pathlib import Path

from src.utilities.constants import SERVICE_NAME


PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
MODEL_FOLDER = Path(PROJECT_ROOT_FOLDER / "machine_learning_models")
app_logger = Logger(service=SERVICE_NAME)
