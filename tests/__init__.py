from pathlib import Path


PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
TEST_ROOT_FOLDER = PROJECT_ROOT_FOLDER / "tests"
TEST_EVENTS_FOLDER = TEST_ROOT_FOLDER / "events"
LOCAL_URL_TILE = "http://localhost:8000/lambda_handler/{z}/{x}/{y}.png"
