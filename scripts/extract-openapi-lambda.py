import json

from samgis import PROJECT_ROOT_FOLDER

if __name__ == '__main__':
    from samgis.utilities.type_hints import ApiRequestBody, ApiResponseBodyFailure, ApiResponseBodySuccess

    with open(PROJECT_ROOT_FOLDER / "docs" / "specs" / "openapi_lambda_wip.json", "w") as output_json:
        json.dump({
            "ApiRequestBody": ApiRequestBody.model_json_schema(),
            "ApiResponseBodyFailure": ApiResponseBodyFailure.model_json_schema(),
            "ApiResponseBodySuccess": ApiResponseBodySuccess.model_json_schema()
        }, output_json)
