FROM registry.gitlab.com/aletrn/gis-prediction:1.12.3

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
COPY --chown=65532:65532 pyproject.toml poetry.lock README.md ${WORKDIR_ROOT}/

# Smoke tests: verify imports and model files present at registry path
RUN ["python3", "-c", "import fastapi; import onnxruntime; import rasterio; import uvicorn; import jinja2; import geopandas"]
RUN python3 -c "
import os
from pathlib import Path
variant = os.environ.get('MODEL_VARIANT', 'sam2.1_hiera_base_plus_uint8')
model_dir = Path('/var/task/.samgis/models') / variant
assert model_dir.is_dir(), f'model dir not found: {model_dir}'
onnx_files = list(model_dir.glob('*.onnx'))
assert len(onnx_files) >= 2, f'expected >=2 .onnx files in {model_dir}, found {len(onnx_files)}'
print(f'model smoke test OK: {model_dir}')
"

USER 65532

CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["/opt/python/bin/python3", "/var/task/client_health.py"]
