from aws_lambda_powertools import Logger
import os
from pathlib import Path

from src.utilities.constants import SERVICE_NAME


PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
MODEL_FOLDER = Path(os.path.join(PROJECT_ROOT_FOLDER, "models"))
app_logger = Logger(service=SERVICE_NAME)
