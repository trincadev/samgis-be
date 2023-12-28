---
title: SamGIS
emoji: 📉
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

## SamGIS - HuggingFace version

Build the docker image this way:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image with the ARG DEPENDENCY_GROUP=fastapi used by poetry
docker build . -f dockerfiles/dockerfile-samgis-base --build-arg DEPENDENCY_GROUP=fastapi --tag localhost/samgis-base-fastapi --progress=plain

# build the image, use the tag "samgis-huggingface"
docker build . --tag localhost/samgis-huggingface --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name samgis-huggingface -p 7860:7860 localhost/samgis-huggingface; docker logs -f samgis-huggingface
```

Test it with curl:

```bash
curl -X 'POST' \
  'http://localhost:7860/infer_samgeo' \
  -H 'accept: application/json' \
  -d '{}'
```

or better visiting the swagger page on http://localhost:7860/docs 


## SamGIS - lambda AWS version

Build the docker image this way:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image with the docker aws repository tag
docker build . -f dockerfiles/dockerfile-samgis-base --build-arg DEPENDENCY_GROUP=aws_lambda --tag localhost/samgis-base-aws-lambda --progress=plain

# build the final docker image
docker build . -f dockerfiles/dockerfile-lambda-fastsam-api --tag localhost/lambda-fastsam-api --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name lambda-fastsam-api -p 8080:8080 lambda-fastsam-api; docker logs -f lambda-fastsam-api
```

Test it with curl:

```bash
URL=http://localhost:8080/2015-03-31/functions/function/invocations
curl -X 'POST' \
  ${URL} \
  -H 'accept: application/json' \
  -d '{}'
```

### Publish the aws lambda docker image
Login on aws ECR with the correct aws profile (change the example `localhost/` repository url with the one from
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

Run the sphinx-apidoc: it's a tool for automatic generation of Sphinx sources that, using the autodoc
extension, document a whole package in the style of other automatic API documentation tools. See the 
[documentation page](https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html) for details.
Run the command from the project root:

```bash
# missing docs folder (run from project root)
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
