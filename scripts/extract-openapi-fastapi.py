# https://www.doctave.com/blog/python-export-fastapi-openapi-spec#step-2-create-an-export-script
import argparse
import json
import logging
import sys

import yaml
from uvicorn.importer import import_from_string

from app import project_root_folder


parser = argparse.ArgumentParser(prog="extract-openapi-fastapi.py")
parser.add_argument("app",       help='App import string. Eg. "main:app"', default="main:app")
parser.add_argument("--app-dir", help="Directory containing the app", default=None)


if __name__ == "__main__":
    # python scripts/extract-openapi.py fastapi_wrapper:app --app-dir wrappers --out docs/specs/openapi_new.yaml
    args = parser.parse_args()

    if args.app_dir is not None:
        logging.info(f"adding {args.app_dir} to sys.path")
        sys.path.insert(0, args.app_dir)

    logging.info(f"importing app from {args.app}")
    app = import_from_string(args.app)
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")

    logging.info(f"writing openapi spec v{version}...")
    output_dir_path = project_root_folder / "docs" / "specs"
    with open(output_dir_path / "output.json", "w") as f:
        json.dump(openapi, f)
    with open(output_dir_path / "output.yaml", "w") as f:
        yaml.dump(openapi, f, sort_keys=False)

    logging.info(f"spec written to {args.out} #")
