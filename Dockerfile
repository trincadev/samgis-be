FROM registry.gitlab.com/aletrn/gis-prediction:v2

# Include global arg in this stage of the build
ARG LAMBDA_TASK_ROOT="/var/task"
ARG PYTHONPATH="${LAMBDA_TASK_ROOT}:${PYTHONPATH}:/usr/local/lib/python3/dist-packages"
ENV VIRTUAL_ENV=${LAMBDA_TASK_ROOT}/.venv \
    PATH="${LAMBDA_TASK_ROOT}/.venv/bin:$PATH"

# Set working directory to function root directory
WORKDIR ${LAMBDA_TASK_ROOT}

COPY samgis ${LAMBDA_TASK_ROOT}/samgis
COPY wrappers ${LAMBDA_TASK_ROOT}/wrappers

RUN ls -l /usr/bin/which
RUN /usr/bin/which python
RUN python -v
RUN echo "PYTHONPATH: ${PYTHONPATH}."
RUN echo "PATH: ${PATH}."
RUN echo "LAMBDA_TASK_ROOT: ${LAMBDA_TASK_ROOT}."
RUN ls -l ${LAMBDA_TASK_ROOT}
RUN ls -ld ${LAMBDA_TASK_ROOT}
RUN ls -l ${LAMBDA_TASK_ROOT}/machine_learning_models
RUN python -c "import sys; print(sys.path)"
RUN python -c "import cv2"
RUN python -c "import fastapi"
RUN python -c "import geopandas"
RUN python -c "import loguru"
RUN python -c "import onnxruntime"
RUN python -c "import rasterio"
RUN python -c "import uvicorn"
RUN df -h
RUN ls -l ${LAMBDA_TASK_ROOT}/samgis/
RUN ls -l ${LAMBDA_TASK_ROOT}/wrappers/
RUN ls -l ${LAMBDA_TASK_ROOT}/static/
RUN ls -l ${LAMBDA_TASK_ROOT}/static/dist
RUN ls -l ${LAMBDA_TASK_ROOT}/static/node_modules

CMD ["uvicorn", "wrappers.fastapi_wrapper:app", "--host", "0.0.0.0", "--port", "7860"]
