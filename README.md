---
title: SamGIS
emoji: 🗺️
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
license: mit
---

## Segment Anything models

It's possible to prepare the model files using <https://github.com/vietanhdev/samexporter/> or using the ones
from <https://huggingface.co/aletrn/sam-quantized> (copy them within the folder `/machine_learning_models`).

## SamGIS - HuggingFace version

The SamGIS HuggingSpace url is <https://huggingface.co/spaces/aletrn/samgis>.
Build the docker image this way:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image from the repository root folder using ARGs:
# - DEPENDENCY_GROUP=fastapi used by poetry
# VITE__MAP_DESCRIPTION, VITE__SAMGIS_SPACE used by 'docker build'
(
  set -o allexport && source <(cat ./static/.env|grep VITE__) && set +o allexport;
  env|grep VITE__;
  docker build . -f dockerfiles/dockerfile-samgis-base --progress=plain \
  --build-arg DEPENDENCY_GROUP=fastapi \
  --build-arg VITE__MAP_DESCRIPTION=${VITE__MAP_DESCRIPTION} \
  --build-arg VITE__SAMGIS_SPACE=${VITE__SAMGIS_SPACE} \
  --tag registry.gitlab.com/aletrn/gis-prediction
)

# build the image, use the tag "samgis-huggingface"
docker build . --tag registry.gitlab.com/aletrn/samgis-huggingface --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name samgis-huggingface -p 7860:7860 registry.gitlab.com/aletrn/samgis-huggingface; docker logs -f samgis-huggingface
```

Test it with curl using a json payload:

```bash
URL=http://localhost:7860/infer_samgis
curl -d@./events/payload_point_eolie.json -H 'accept: application/json' ${URL}
```

or better visiting the swagger page on <http://localhost:7860/docs>

## SamGIS - lambda AWS version

Build the docker image this way:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image with the docker aws repository tag
docker build . -f dockerfiles/dockerfile-samgis-base --build-arg DEPENDENCY_GROUP=aws_lambda \
  --tag example-docker-namespace/samgis-base-aws-lambda --progress=plain

# build the final docker image
docker build . -f dockerfiles/dockerfile-lambda-fastsam-api --tag example-docker-namespace/lambda-fastsam-api --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name lambda-fastsam-api -p 8080:8080 lambda-fastsam-api; docker logs -f lambda-fastsam-api
```

Test it with curl using a json payload:

```bash
URL=http://localhost:8080/2015-03-31/functions/function/invocations
curl -d@./events/payload_point_eolie.json -H 'accept: application/json' ${URL}
```

### Publish the aws lambda docker image

Login on aws ECR with the correct aws profile (change the example `example-docker-namespace/` repository url with the one from
the [ECR push command instructions page](https://eu-west-1.console.aws.amazon.com/ecr/repositories/)).

### Dependencies installation and local tests

The docker build process needs only the base dependency group plus the `aws_lambda` or `fastapi` optional one.
Install also the `test` and/or `docs` groups if needed.

### Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
python -m pytest --cov=samgis --cov-report=term-missing && coverage html
```

### How to update the static documentation with sphinx

This project documentation uses sphinx-apidoc: it's a tool for automatic generation of Sphinx sources that, using the autodoc
extension, document a whole package in the style of other automatic API documentation tools. See the
[documentation page](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) for details.
Run the command from the project root:

```bash
# missing docs folder (run from project root) initialize this way
cd docs && sphinx-quickstart -p SamGIS -r 1.0.0 -l python --master index

# update docs folder (from project root)
sphinx-apidoc -f -o docs samgis
```

Then it's possible to generate the HTML pages

```bash
cd docs && make html && ../

# to clean old files
cd docs && make clean html && cd ../
```

The static documentation it's now ready at the path `docs/_build/html/index.html`.

To create a work in progress openapi json or yaml file use

- `extract-openapi-fastapi.py`
- `extract-openapi-lambda.py` (useful to export the json schema request and response from lambda app api)
