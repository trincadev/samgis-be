# Changelog

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
