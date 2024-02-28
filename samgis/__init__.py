"""Get machine learning predictions from geodata raster images"""
import os

# not used here but contextily_tile is imported in samgis.io.tms2geotiff
from contextily import tile as contextily_tile
from pathlib import Path
from samgis.utilities.constants import SERVICE_NAME

PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
MODEL_FOLDER = Path(PROJECT_ROOT_FOLDER / "machine_learning_models")

IS_AWS_LAMBDA = bool(os.getenv("IS_AWS_LAMBDA", ""))

if IS_AWS_LAMBDA:
    try:
        from aws_lambda_powertools import Logger

        app_logger = Logger(service=SERVICE_NAME)
    except ModuleNotFoundError:
        print("this should be AWS LAMBDA environment but we miss the required aws lambda powertools package")
else:
    from samgis_core.utilities.fastapi_logger import setup_logging

    app_logger = setup_logging(debug=True)
