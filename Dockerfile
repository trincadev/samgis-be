FROM registry.gitlab.com/aletrn/gis-prediction:1.12.4

ARG WORKDIR_ROOT="/var/task"
ARG MODEL_VARIANT="sam2.1_hiera_base_plus_uint8"
ENV VIRTUAL_ENV=${WORKDIR_ROOT}/.venv \
    PATH="${WORKDIR_ROOT}/.venv/bin:/opt/python/bin:$PATH" \
    WRITE_TMP_ON_DISK="" \
    VITE__STATIC_INDEX_URL="/static" \
    VITE__INDEX_URL="/" \
    MODEL_VARIANT=${MODEL_VARIANT} \
    MODEL_FOLDER="${WORKDIR_ROOT}/.samgis/models/${MODEL_VARIANT}"

WORKDIR ${WORKDIR_ROOT}

COPY --chown=65532:65532 app.py ${WORKDIR_ROOT}/
COPY --chown=65532:65532 pyproject.toml README.md ${WORKDIR_ROOT}/

# Smoke tests: verify imports and model files present at registry path
RUN ["python3", "-c", "import fastapi"]
RUN ["python3", "-c", "import onnxruntime"]
RUN ["python3", "-c", "import rasterio"]
RUN ["python3", "-c", "import uvicorn"]
RUN ["python3", "-c", "import jinja2"]
RUN ["python3", "-c", "import geopandas"]
RUN ["python3", "-c", "from pathlib import Path; model_dir = Path('/var/task/.samgis/models/sam2.1_hiera_base_plus_uint8'); assert model_dir.is_dir(), f'model dir not found: {model_dir}'"]
RUN ["python3", "-c", "from pathlib import Path; onnx_files = list(Path('/var/task/.samgis/models/sam2.1_hiera_base_plus_uint8').glob('*.onnx')); assert len(onnx_files) >= 2, f'expected >=2 .onnx files, found {len(onnx_files)}'"]

USER 65532

CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["/opt/python/bin/python3", "/var/task/client_health.py"]
