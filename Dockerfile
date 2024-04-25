FROM registry.gitlab.com/aletrn/gis-prediction:1.5.0

# Include global arg in this stage of the build
ARG WORKDIR_ROOT="/var/task"
ARG PYTHONPATH="${WORKDIR_ROOT}:${PYTHONPATH}:/usr/local/lib/python3/dist-packages"
ENV VIRTUAL_ENV=${WORKDIR_ROOT}/.venv \
    PATH="${WORKDIR_ROOT}/.venv/bin:$PATH"
ENV IS_AWS_LAMBDA=""

# Set working directory to function root directory
WORKDIR ${WORKDIR_ROOT}

COPY samgis ${WORKDIR_ROOT}/samgis
COPY wrappers ${WORKDIR_ROOT}/wrappers
COPY pyproject.toml poetry.lock README.md ${WORKDIR_ROOT}
RUN . ${WORKDIR_ROOT}/.venv && which python && echo "# install samgis #" && pip install .
RUN mkdir ${WORKDIR_ROOT}/vis_output

RUN ls -l /usr/bin/which
RUN /usr/bin/which python
RUN python --version
RUN pip list
RUN echo "PYTHONPATH: ${PYTHONPATH}."
RUN echo "PATH: ${PATH}."
RUN echo "WORKDIR_ROOT: ${WORKDIR_ROOT}."
RUN ls -l ${WORKDIR_ROOT}
RUN ls -ld ${WORKDIR_ROOT}
RUN ls -l ${WORKDIR_ROOT}/machine_learning_models
RUN python -c "import sys; print(sys.path)"
RUN python -c "import cv2"
RUN python -c "import fastapi"
RUN python -c "import geopandas"
RUN python -c "import loguru"
RUN python -c "import onnxruntime"
RUN python -c "import rasterio"
RUN python -c "import uvicorn"
RUN python -c "import jinja2"
RUN df -h
RUN ls -l ${WORKDIR_ROOT}/samgis/
RUN ls -l ${WORKDIR_ROOT}/wrappers/
RUN ls -l ${WORKDIR_ROOT}/static/
RUN ls -l ${WORKDIR_ROOT}/static/dist
RUN ls -l ${WORKDIR_ROOT}/static/node_modules
RUN ls -l ${WORKDIR_ROOT}/vis_output

CMD ["uvicorn", "wrappers.fastapi_wrapper:app", "--host", "0.0.0.0", "--port", "7860"]
