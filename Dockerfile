FROM registry.gitlab.com/aletrn/gis-prediction:1.12.3

ARG WORKDIR_ROOT="/var/task"
ENV VIRTUAL_ENV=${WORKDIR_ROOT}/.venv \
    PATH="${WORKDIR_ROOT}/.venv/bin:/opt/python/bin:$PATH" \
    WRITE_TMP_ON_DISK="" \
    VITE__STATIC_INDEX_URL="/static" \
    VITE__INDEX_URL="/"

WORKDIR ${WORKDIR_ROOT}

COPY --chown=65532:65532 app.py ${WORKDIR_ROOT}/
COPY --chown=65532:65532 pyproject.toml poetry.lock README.md ${WORKDIR_ROOT}/

# Smoke tests: verify imports and model files
RUN ["python3", "-c", "import fastapi; import onnxruntime; import rasterio; import uvicorn; import jinja2; import geopandas"]
RUN ["python3", "-c", "from pathlib import Path; assert Path('/var/task/sam-quantized/machine_learning_models').is_dir()"]

USER 65532

CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["/opt/python/bin/python3", "/var/task/client_health.py"]
