import json

from app import project_root_folder
from samgis_web.utilities.type_hints import ApiRequestBody, ApiResponseBodyFailure, ApiResponseBodySuccess


if __name__ == '__main__':
    with open(project_root_folder / "docs" / "specs" / "openapi_lambda_wip.json", "w") as output_json:
        json.dump({
            "ApiRequestBody": ApiRequestBody.model_json_schema(),
            "ApiResponseBodyFailure": ApiResponseBodyFailure.model_json_schema(),
            "ApiResponseBodySuccess": ApiResponseBodySuccess.model_json_schema()
        }, output_json)
