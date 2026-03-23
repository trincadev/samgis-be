# CLAUDE.md

See [AGENTS.md](./AGENTS.md) for agent instructions.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SamGIS is a backend service for machine learning instance segmentation on geospatial data using the Segment Anything Model (SAM). The project provides both a FastAPI backend and a Vue.js frontend for interactive map-based segmentation.

**Key Architecture:**
- Backend: FastAPI application (`app.py`) that exposes inference endpoints
- Frontend: Vue.js SPA in `static/` directory using Leaflet for maps
- ML Models: SAM2 ONNX weights from HuggingFace (`aletrn/sam2-onnx-weights`), downloaded via `scripts/download_models.py`
- External Dependencies: Uses `samgis_core` and `samgis_web` packages (not in repo)
- Deployment: Multi-stage Docker builds for production, supports HuggingFace Spaces

**Note:** For frontend-specific development (Vue.js, Leaflet, Tailwind), see `static/CLAUDE.md`.

## Development Setup

### Initial Setup

```bash
# Install Python dependencies
uv sync --group test --group docs

# Download SAM2 model weights (default: sam2.1_hiera_base_plus_uint8)
uv run python scripts/download_models.py
# Override variant: MODEL_VARIANT=sam2.1_hiera_tiny_uint8 uv run python scripts/download_models.py
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

**E2E smoke tests** (from `static/` directory, requires Docker container running on `:7860`):
```bash
# Run smoke tests against Docker container
pnpm test:e2e:smoke

# Run all e2e tests against Vite dev server (backend tests auto-skip)
pnpm test:e2e
```

### Docker Development

**Build base image:**
```bash
# Extract version from pyproject.toml and build
SAMGIS_BASE_DOCKER_VERSION=$(grep version pyproject.toml |head -1|cut -d'=' -f2|cut -d'"' -f2)
set -o allexport && source <(cat ./static/.env|grep VITE__) && set +o allexport

docker build . -f dockerfiles/dockerfile-samgis-base --progress=plain \
  --build-arg VITE__MAP_DESCRIPTION="${VITE__MAP_DESCRIPTION}" \
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
  - `/health`: Health check endpoint - verifies model files via SHA-256 checksums
  - `/infer_samgis`: POST endpoint for ML inference
  - Middleware: CORS, logging, correlation ID tracking

- External packages (installed via uv):
  - `samgis_core`: Core ML prediction logic, utilities
  - `samgis_web`: Web helpers, type hints, middlewares

- `scripts/`: Utility scripts
  - `download_models.py`: Download SAM2 model weights with SHA-256 verification
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
- `dockerfiles/dockerfile-samgis-base`: Multi-stage base image using Docker Hardened Images (`dhi.io/python:3.13`)
  - Builder: `dhi.io/python:3.13-dev` (has `apt`, `pip`, shell)
  - Runtime: `dhi.io/python:3.13` (no shell, no pkg manager, `nonroot` user 65532)
  - `libexpat` copied from builder (required by rasterio's bundled GDAL)
  - No libGL or system GDAL needed (manylinux wheels bundle everything)
- `dockerfiles/dockerfile-samgis-base-alpinelinux3.23`: Alpine Linux POC (not production). Documents how to build onnxruntime on Alpine with `apk` system packages (`py3-onnxruntime`, `gdal-dev`). Last updated in `be6b0b0`. Superseded by DHI base for production use.

### Model Files

- SAM2 ONNX weights from [aletrn/sam2-onnx-weights](https://huggingface.co/aletrn/sam2-onnx-weights)
  - Default variant: `sam2.1_hiera_base_plus_uint8` (~73 MB)
  - Downloaded to `~/.samgis/models/<variant>/` via `scripts/download_models.py`
  - Each variant contains `encoder.onnx`, `decoder.onnx`, `metadata.json`
  - SHA-256 checksums verified on download and in `/health` endpoint
  - Override variant via `MODEL_VARIANT` env, override path via `MODEL_FOLDER` env

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

**Known Issue:** Sphinx autodoc fails to import `samgis_web.web` modules (`exception_handlers`, `middlewares`) due to pydantic 2.10+ being incompatible with fastapi 0.128.x during type evaluation at import time. This only affects Sphinx builds, not runtime. The workaround is `autodoc_mock_imports` in `docs/conf.py` which mocks `fastapi` and `starlette` during the doc build.

## Dependency Management

### Updating requirements.txt from uv

```bash
# Export production dependencies with hashes to requirements.txt
uv export --frozen --no-dev --no-emit-project --output-file requirements.txt
```

### Dependency Groups

- Default: Core dependencies (onnxruntime, samgis-web)
- `test`: pytest, pytest-cov, httpx, python-dotenv
- `dev`: pyright
- `docs`: sphinx, sphinx-autodoc-typehints

## Key Environment Variables

- `WORKDIR`: Working directory (default: project root)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MODEL_VARIANT`: SAM2 model variant (default: `sam2.1_hiera_base_plus_uint8`)
- `MODEL_FOLDER`: Override model directory path (default: `~/.samgis/models/<variant>`)
- `WRITE_TMP_ON_DISK`: Path to mount temporary output files
- `VITE__MAP_DESCRIPTION`: Map description text (frontend, optional)
- `VITE_INDEX_URL`: Base URL path for the frontend app (default: `/`)

## HuggingFace Spaces Deployment

The project is deployed at https://huggingface.co/spaces/aletrn/samgis using Docker SDK.

System dependencies: Add to `pre-requirements.txt` (Debian packages).
