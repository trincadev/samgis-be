# Changelog

## Version 1.11.6

- fix the tailwindcss build command within the docker image

## Version 1.11.5

- pin sphinx version < 8.2.0 to avoid a failure on docs build, see https://github.com/tox-dev/sphinx-autodoc-typehints/issues/523 (sphinx-autodoc-typehints 3.2.0 at the moment doesn't resolve this issue)
- updated docs because of removed `samgis_core.utilities.update_requirements_txt` module

## Version 1.11.4

- Update backend dependencies (samgis-core==3.3.1, samgis-web==1.2.5)
- Update frontend dependecies
- fixed build:tailwindcss command (now it's using @tailwindcss/cli)

I forgot to report some minor versions, sorry =)

## Version 1.8.2

- Update frontend dependencies
- update backend dependencies (samgis-core = 3.1.1, samgis-web = 1.1.2, gradio == 5.5.0, numpy == 2.1.3, onnxruntime==1.20.0, starlette == 0.41.2)
- base dockerfile: install `libexpat1` Debian package to avoid the `Cannot open library: libexpat.so.1: cannot open shared object file: No such file or directory` error on `rasterio` python import

## Version 1.8.0

- Update frontend dependencies
- update backend dependencies (samgis-core = 3.0.17, samgis-web = 1.0.16, gradio == 5.1.0, numpy == 2.1.2, starlette == 0.40.0, max python version == 3.12)
- update poetry == 1.8.4
- update Dockerfile to use the python base version == 3.12-bookworm
- update README.md because of updated command to create an already tagged docker image

## Version 1.7.1

- Update frontend dependencies
- remove backend dependencies already installed by samgis-web (samgis-core = 3.0.17, samgis-web = 1.0.16)
- update Dockerfile, README.md because of added optional gradio poetry dependency group (useful only in case of local tests on the HuggingFace page)

## Version 1.7.0

- Update frontend dependencies
- remove backend dependencies already installed by samgis-web (samgis-core = 3.0.14, samgis-web = 1.0.14)
- remove poetry dependency groups 'fastapi' and 'gradio'
- update Dockerfile, README.md because of removed fastapi poetry dependency group

## Version 1.6.10

- Update frontend dependencies
- update backend dependencies

## Version 1.6.9

- Update samgis-core = 3.0.12, samgis-web = 1.0.13

## Version 1.6.8

- Update samgis-core = 3.0.9, samgis-web = 1.0.10
- now in samgis-core there is get_dependencies_freeze(), a function that write an updated requirements.txt starting 
  from current installed packages

## Version 1.6.7

- Update samgis-core = 3.0.8, samgis-web = 1.0.9
- move frontend_builder from samgis-web to samgis-core but expose it also within samgis_web.utilities
- create_requirements.sh: handle case of of missing ./tmp/ folder
- update docs

## Version 1.6.6

- Adopt again docker SDK (we'll try Gradio SDK on duplicated HuggingFace space)

## Version 1.6.5

- add missing files needed for HuggingFace ci
- using samgis-core = 3.0.6, samgis-web = 1.0.8
- updated sam-quantized submodule because of updated decoder model
- trying to adopt Gradio SDK

## Version 1.6.0

- move all the helper functions to samgis_web (version 1.0.6) to avoid code duplication between different demos
- update backend and frontend dependencies (samgis-core updated to version 3.0.5)
- samgis_core 3.0.5 now exposes ``setup_logger()` based on `structlog` package to improve logging with correlation id
  (that's not working with functions called from gradio interfaces)
- SamGIS now can work using Gradio SDK on huggingface (if needed change the README.md file accordingly)

## Version 1.5.4

- update backend and frontend dependencies (samgis-core updated to version 2.0.2)

## Version 1.5.3

- update backend and frontend dependencies (samgis-core updated to version 2.0.1)

## Version 1.5.2

- update backend and frontend dependencies

## Version 1.5.1

- samgis_core: now support onnxruntime 1.17.x and later
- samgis_core: remove opencv-python dependency, now SegmentAnythingONNX2 resize images using PIL
- samgis_core: bump to version 2.0.0 to remark a breaking change: passage from SegmentAnythingONNX to SegmentAnythingONNX2
- known issue: on MacOS, samgis still work without executing it within a docker container, but it's slower during image embedding because of a memory leak caused by CoreML

## Version 1.5.0

- now it's possible to download tmp images from /vis_output routes if WRITE_TMP_ON_DISK env variable exists (it's the output folder path)

## Version 1.4.2

- frontend: add support for hiding old polygon layers from ML inferences

## Version 1.4.1

- update base python docker image to bookworm-3.11
- move support for AWS lambda (aws-lambda-rie, lambda-entrypoint.sh) docker to separated dockerfile
- add Demo url entry in pyproject.toml file

## Version 1.4.0

- add support for python 3.11
- add urls section used by [pypi.org](https://pypi.org/)
- update some vulnerable dependencies
- update samgis_core@1.2.0 to use python 3.11

## Version 1.3.0

- take advantage of re-usable image embeddings in SAM model using samgis_core@1.1.2
- add map navigation locking (unlockable!) on ML request to take advantage of image embedding re-use
- add a metadata section within the pyproject.toml file
- handle case of samgis not installed within the docker image that could crash the backend on /health requests

## Version 1.2.2

- update dependencies version

## Version 1.2.1

- update dependencies version

## Version 1.2.0

- code refactor to separate core functionality (instance segmentation) from other code
- updated test coverage

## Version 1.1.0

- Added this changelog
- specific backend branch code uses terrain providers like nextzen and MapBox Terrain-RGB v1
- update test coverage
- update python dependencies versions
- update node dependencies versions

## Version 1.0.2

- HuggingFace frontend demo: update the navbar url to SamGIS docs
- add two openapi docs builder scripts
- update samgis version within docs
- remove unused package.json

## Version 1.0.1

- fixed zlib1g security vulnerability in python:3.11-slim-bookworm docker image, see <https://security-tracker.debian.org/tracker/CVE-2023-45853>

## Version 1.0.0

First release:

- user onboarding tour with driver.js
- code decoupling between the AWS lambda wrapper and the backend...
- ...now also deployed on this HuggingSpace space demo (here some explanation about adding a SPA vuejs frontend)
- request input validation using Pydantic
- support for array prompts (both rectangle and point types)
- tiles download/merge/crop steps uses contextily by geopandas
- CSS frontend style with Tailwind
