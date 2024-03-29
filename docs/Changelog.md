# Changelog

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
- fixed zlib1g security vulnerability in python:3.11-slim-bookworm docker image, see https://security-tracker.debian.org/tracker/CVE-2023-45853

## Version 1.0.0
First release:
- user onboarding tour with driver.js
- code decoupling between the AWS lambda wrapper and the backend...
- ...now also deployed on this HuggingSpace space demo (here some explanation about adding a SPA vuejs frontend)
- request input validation using Pydantic
- support for array prompts (both rectangle and point types)
- tiles download/merge/crop steps uses contextily by geopandas
- CSS frontend style with Tailwind
