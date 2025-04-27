FROM registry.gitlab.com/aletrn/gis-prediction:1.11.7

# Include global arg in this stage of the build
ARG WORKDIR_ROOT="/var/task"
ENV VIRTUAL_ENV=${WORKDIR_ROOT}/.venv PATH="${WORKDIR_ROOT}/.venv/bin:$PATH"
ENV WRITE_TMP_ON_DISK=""
ENV MOUNT_GRADIO_APP=""
ENV VITE__STATIC_INDEX_URL="/static"
ENV VITE__INDEX_URL="/"
ENV HOME_USER=/home/python

# Set working directory to function root directory
WORKDIR ${WORKDIR_ROOT}
# workaround for missing /home folder
RUN ls -ld ${HOME_USER}
RUN ls -lA ${HOME_USER}

COPY --chown=python:python app.py ${WORKDIR_ROOT}/
COPY --chown=python:python pyproject.toml poetry.lock README.md ${WORKDIR_ROOT}
# RUN . ${WORKDIR_ROOT}/.venv && which python && echo "# install samgis #" && pip install .
RUN if [ "${WRITE_TMP_ON_DISK}" != "" ]; then mkdir {WRITE_TMP_ON_DISK}; fi
RUN if [ "${WRITE_TMP_ON_DISK}" != "" ]; then ls -l {WRITE_TMP_ON_DISK}; fi

RUN ls -l /usr/bin/which
RUN /usr/bin/which python
RUN python --version
RUN pip list
RUN echo "PATH: ${PATH}."
RUN echo "WORKDIR_ROOT: ${WORKDIR_ROOT}."
RUN ls -l ${WORKDIR_ROOT}
RUN ls -ld ${WORKDIR_ROOT}
RUN ls -l ${WORKDIR_ROOT}/machine_learning_models
RUN python -c "import sys; print(sys.path)"
RUN python -c "import fastapi"
RUN python -c "import geopandas"
RUN python -c "import onnxruntime"
RUN python -c "import rasterio"
RUN python -c "import uvicorn"
RUN python -c "import jinja2"
RUN df -h
RUN ls -l ${WORKDIR_ROOT}/app.py
RUN ls -l ${WORKDIR_ROOT}/static/
RUN ls -l ${WORKDIR_ROOT}/static/dist
RUN ls -l ${WORKDIR_ROOT}/static/node_modules

USER 999

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD curl -f http://localhost:7860/health
