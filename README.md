---
title: SamGIS
emoji: 🗺️
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# About this README

I tested these instructions on macOS, but should work on linux as well.

## Segment Anything models

It's possible to prepare the model files using <https://github.com/vietanhdev/samexporter/> or using the ones
from <https://huggingface.co/aletrn/sam-quantized> (copy them within the folder `/machine_learning_models`).

In this case after the clone of this repository it's best to initialize the `sam-quantized` submodule:

```bash
git submodule update --init --recursive
```

## SamGIS - Gradio SDK version

After developed your project using [the gradio quickstart](https://www.gradio.app/guides/quickstart),
you can declare the specific gradio version you want to use in the HuggingFace space using
the README.md header section. You need to compile these fields:

```
sdk: gradio
sdk_version: [current Gradio version, e.g. 4.44.0]
app_file: app.py
```

For some reason the space won't work if the app_file setting points to a file not
within the root folder project.

Under the hood, HuggingFace install the gradio SDK using docker. If you need to install some dependencies
(for this project I needed `nodejs`) you can add some system
[debian packages](https://huggingface.co/docs/hub/spaces-dependencies#adding-your-own-dependencies)
within the `pre-requirements.txt` file.

If you want to run locally the project not from a docker container you can install the optional gradio poetry group like this:

```bash
poetry install --with gradio --with --no-root
```


## SamGIS - Docker version

The SamGIS HuggingSpace url is <https://huggingface.co/spaces/aletrn/samgis>.
Build the docker image this way:

```bash
# clean any old active containers
docker stop $(docker ps -a -q); docker rm $(docker ps -a -q)

# build the base docker image from the repository root folder.
# The SAMGIS_BASE_DOCKER_VERSION env variable read from the pyproject.toml is used to tag the docker image
(
  SAMGIS_BASE_DOCKER_VERSION=$(grep version pyproject.toml |head -1|cut -d'=' -f2|cut -d'"' -f2);
  set -o allexport && source <(cat ./static/.env|grep VITE__) && set +o allexport;
  env|grep VITE__;
  docker build . -f dockerfiles/dockerfile-samgis-base --progress=plain \
  --build-arg VITE__MAP_DESCRIPTION="${VITE__MAP_DESCRIPTION}" \
  --build-arg VITE__SAMGIS_SPACE="${VITE__SAMGIS_SPACE}" \
  --build-arg VITE__STATIC_INDEX_URL="${VITE__STATIC_INDEX_URL}" \
  --tag registry.gitlab.com/aletrn/gis-prediction:${SAMGIS_BASE_DOCKER_VERSION}
)

# build the image, use the tag "samgis-huggingface"
docker build . --tag registry.gitlab.com/aletrn/samgis-huggingface --progress=plain
```

Run the container (keep it on background) and show logs

```bash
docker run  -d --name samgis-huggingface -p 7860:7860 \
  -e VITE__STATIC_INDEX_URL=${VITE__STATIC_INDEX_URL} \
  -e VITE__INDEX_URL=${VITE__INDEX_URL} \
  -e MOUNT_GRADIO_APP="" \
  registry.gitlab.com/aletrn/samgis-huggingface; docker logs -f samgis-huggingface
```

Test it with curl using a json payload:

```bash
URL=http://localhost:7860/infer_samgis
curl -d@./events/payload_point_eolie.json -H 'content-type: application/json' ${URL}
```

or better visiting the swagger page on <http://localhost:7860/docs>

### Dependencies installation, local execution and local tests

The docker build process needs only the base dependency group plus the `aws_lambda` or `fastapi` optional one (right now I use almost only the `fastapi` version). Install also the `test` and/or `docs` groups if needed.

#### Local execution

If you need to use the SPA frontend follow the frontend instruction [here](/static/README.md).

You can run the local server using this python command:

```python
uvicorn app:app --host 127.0.0.1 --port 7860
```

Change the port and/or the host ip if needed. Test it with curl using a json payload:

```bash
URL=http://localhost:7860/infer_samgis
curl -d@./events/payload_point_eolie.json -H 'content-type: application/json' ${URL}
```

#### Local execution on MacOS

There is a known issue running the project on macOS. SamGIS still work also without executing it within a docker container, but is slower during image embedding because of a memory leak caused by CoreML. Here a log about this bug:

```less
[...]
2024-05-15T18:38:37.478698+0200 - INFO - predictors.py - samexporter_predict - (be2506dc-0887-4752-9889-cf12db7501f5) missing instance model mobile_sam, instantiating it now! 
2024-05-15T18:38:37.479582+0200 - INFO - sam_onnx2.py - __init__ - (be2506dc-0887-4752-9889-cf12db7501f5) Available providers for ONNXRuntime: %s 
2024-05-15 18:38:37.673229 [W:onnxruntime:, coreml_execution_provider.cc:81 GetCapability] CoreMLExecutionProvider::GetCapability, number of partitions supported by CoreML: 104 number of nodes in the graph: 566 number of nodes supported by CoreML: 383
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
2024-05-15T18:38:47.691608+0200 - INFO - sam_onnx2.py - __init__ - (be2506dc-0887-4752-9889-cf12db7501f5) encoder_input_name: 
2024-05-15 18:38:47.913677 [W:onnxruntime:, coreml_execution_provider.cc:81 GetCapability] CoreMLExecutionProvider::GetCapability, number of partitions supported by CoreML: 48 number of nodes in the graph: 496 number of nodes supported by CoreML: 221
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
Context leak detected, CoreAnalytics returned false
2024-05-15T18:38:50.926801+0200 - DEBUG - predictors.py - samexporter_predict - (be2506dc-0887-4752-9889-cf12db7501f5) using a mobile_sam instance model... 
[...]
```

This problem doesn't rise if running it within the docker container.

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
# 
cd docs && sphinx-quickstart --project SamGIS --release 1.0.0 --language python --master index

# update docs folder (from project root) referring to the other packages folder
sphinx-apidoc -f -o docs /path/to/samgis_web
sphinx-apidoc -f -o docs /path/to/samgis_core
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
