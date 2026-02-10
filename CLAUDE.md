# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SamGIS is a backend service for machine learning instance segmentation on geospatial data using the Segment Anything Model (SAM). The project provides both a FastAPI backend and a Vue.js frontend for interactive map-based segmentation.

**Key Architecture:**
- Backend: FastAPI application (`app.py`) that exposes inference endpoints
- Frontend: Vue.js SPA in `static/` directory using Leaflet for maps
- ML Models: SAM quantized models stored in `sam-quantized/` git submodule
- External Dependencies: Uses `samgis_core` and `samgis_web` packages (not in repo)
- Deployment: Multi-stage Docker builds for production, supports HuggingFace Spaces

**Note:** For frontend-specific development (Vue.js, Leaflet, Tailwind), see `static/CLAUDE.md`.

## Development Setup

### Initial Setup

```bash
# Initialize SAM model submodule (required)
git submodule update --init --recursive

# Install Python dependencies
poetry install --with test --with docs --no-root
```

### Running Locally

**Backend:**
```bash
# Start FastAPI server
uvicorn app:app --host 127.0.0.1 --port 7860

# Visit swagger docs at http://localhost:7860/docs
```

**Frontend:** See `static/CLAUDE.md` for detailed frontend development instructions.

**Known macOS Issue:** Running locally on macOS causes slower embedding due to CoreML memory leak. Use Docker to avoid this.

### Testing

```bash
# Run tests with coverage
python -m pytest --cov=samgis --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=samgis --cov-report=term-missing && coverage html
# Report available at htmlcov/index.html
```

Test files are in `tests/`. Configuration in `pyproject.toml` covers `scripts/` and `app.py`.

### Docker Development

**Build base image:**
```bash
# Extract version from pyproject.toml and build
SAMGIS_BASE_DOCKER_VERSION=$(grep version pyproject.toml |head -1|cut -d'=' -f2|cut -d'"' -f2)
set -o allexport && source <(cat ./static/.env|grep VITE__) && set +o allexport

docker build . -f dockerfiles/dockerfile-samgis-base --progress=plain \
  --build-arg VITE__MAP_DESCRIPTION="${VITE__MAP_DESCRIPTION}" \
  --build-arg VITE__SAMGIS_SPACE="${VITE__SAMGIS_SPACE}" \
  --build-arg VITE__STATIC_INDEX_URL="${VITE__STATIC_INDEX_URL}" \
  --tag registry.gitlab.com/aletrn/gis-prediction:${SAMGIS_BASE_DOCKER_VERSION}
```

**Build and run application image:**
```bash
# Build
docker build . --tag registry.gitlab.com/aletrn/samgis-huggingface --progress=plain

# Run container
docker run -d --name samgis-huggingface -p 7860:7860 \
  -e VITE__STATIC_INDEX_URL=${VITE__STATIC_INDEX_URL} \
  -e VITE__INDEX_URL=${VITE__INDEX_URL} \
  -e MOUNT_GRADIO_APP="" \
  registry.gitlab.com/aletrn/samgis-huggingface

# Follow logs
docker logs -f samgis-huggingface
```

**Test with curl:**
```bash
URL=http://localhost:7860/infer_samgis
curl -d@./events/payload_point_eolie.json -H 'content-type: application/json' ${URL}
# or:
curl -d@./events/payload_point_colico.json -H 'content-type: application/json' ${URL}
```

## Code Architecture

### Backend Structure

- `app.py`: Main FastAPI application with inference endpoints
  - `/health`: Health check endpoint - verifies model files exist
  - `/infer_samgis`: POST endpoint for ML inference
  - Middleware: CORS, logging, correlation ID tracking

- External packages (installed via poetry):
  - `samgis_core`: Core ML prediction logic, utilities
  - `samgis_web`: Web helpers, type hints, middlewares

- `scripts/`: Utility scripts
  - `extract-openapi-fastapi.py`: Export OpenAPI spec
  - `extract-openapi-lambda.py`: Export Lambda API schema
  - `client_health.py`: Health check client

- `tests/`: Test suite
  - `test_app.py`: Application tests
  - `test_client_health.py`: Health check tests
  - `events/`: Example request/response payloads

### Frontend Structure

- `static/`: Vue.js SPA with Vite - **see `static/CLAUDE.md` for detailed documentation**
  - Main component: `src/components/PagePredictionMap.vue` (Leaflet map + ML inference)
  - State management: `src/components/constants.ts` (reactive refs)
  - Tech stack: Vue 3, TypeScript, Leaflet, Tailwind CSS, driver.js
  - API integration: POST `/infer_samgis` with bbox and prompts

### Docker Structure

- `Dockerfile`: Main application image (uses pre-built base)
- `dockerfiles/dockerfile-samgis-base`: Multi-stage base image with all dependencies
- `dockerfiles/dockerfile-samgis-base-alpinelinux3.23`: Alpine Linux variant

### Model Files

- `sam-quantized/`: Git submodule with quantized SAM models
  - Must be initialized after clone: `git submodule update --init --recursive`
  - Contains encoder and decoder ONNX models
  - Alternative: prepare models using samexporter or HuggingFace

## Documentation

### Building Sphinx Docs

```bash
# Generate API documentation
sphinx-apidoc -f -o docs /path/to/samgis_web
sphinx-apidoc -f -o docs /path/to/samgis_core

# Build HTML docs
cd docs && make html && cd ../

# Clean and rebuild
cd docs && make clean html && cd ../

# Output at: docs/_build/html/index.html
```

**Known Issue:** Sphinx autodoc fails to import `samgis_web.web` modules (`exception_handlers`, `gradio_helpers`, `middlewares`) due to pydantic 2.10+ being incompatible with fastapi 0.128.x during type evaluation at import time. This only affects Sphinx builds, not runtime. The workaround is `autodoc_mock_imports` in `docs/conf.py` which mocks `fastapi`, `gradio`, and `starlette` during the doc build.

## Dependency Management

### Updating requirements.txt from Poetry

```bash
# Export specific packages to requirements.txt
poetry export --without-hashes --format=requirements.txt | \
  grep -w -E "$(sed -z -e 's/\n/=|/g' requirements_no_versions.txt)" > requirements.txt
```

Note: Avoid newlines after last package in `requirements_no_versions.txt`.

### Poetry Groups

- Default: Core dependencies (onnxruntime, samgis-web)
- `gradio` (optional): For gradio SDK version
- `test` (optional): pytest, pytest-cov, httpx
- `docs` (optional): sphinx, sphinx-autodoc-typehints

## Key Environment Variables

- `WORKDIR`: Working directory (default: project root)
- `LOG_LEVEL`: Logging level (default: INFO)
- `WRITE_TMP_ON_DISK`: Path to mount temporary output files
- `MOUNT_GRADIO_APP`: Enable gradio app mounting
- `VITE__*`: Frontend configuration variables (sourced from static/.env)

## HuggingFace Spaces Deployment

The project is deployed at https://huggingface.co/spaces/aletrn/samgis

For Gradio SDK version, set in README.md header:
```yaml
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
```

System dependencies: Add to `pre-requirements.txt` (Debian packages).
