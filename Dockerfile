# inspired by https://dev.to/gaborschulz/running-python-311-on-aws-lambda-1i7p
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.7.2 as build-image

LABEL maintainer="alessandro trinca <alessandro@trinca.tornidor.com>"

# Include global arg in this stage of the build
ARG LAMBDA_TASK_ROOT="/var/task"
ARG PYTHONPATH="${LAMBDA_TASK_ROOT}:${PYTHONPATH}:/usr/local/lib/python3/dist-packages"

RUN mkdir -p ${LAMBDA_TASK_ROOT}

# Install aws-lambda-cpp build dependencies
RUN apt update && \
  apt install -y g++ make cmake unzip libcurl4-openssl-dev python3-pip

# install required packages
COPY requirements_pip.txt ${LAMBDA_TASK_ROOT}/
RUN python -m pip install --target ${LAMBDA_TASK_ROOT} --upgrade -r ${LAMBDA_TASK_ROOT}/requirements_pip.txt
RUN python -m pip install torch torchvision --target ${LAMBDA_TASK_ROOT} --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN python -m pip install --target ${LAMBDA_TASK_ROOT} -r ${LAMBDA_TASK_ROOT}/requirements.txt

FROM osgeo/gdal:ubuntu-small-3.7.2

# Include global arg in this stage of the build
ARG LAMBDA_TASK_ROOT="/var/task"
ARG PYTHONPATH="${LAMBDA_TASK_ROOT}:${PYTHONPATH}:/usr/local/lib/python3/dist-packages"
ARG RIE="https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie"

# Set working directory to function root directory
WORKDIR ${LAMBDA_TASK_ROOT}

RUN apt update && apt install -y libgl1 curl
RUN ls -ld /usr/lib/x86_64-linux-gnu/libGL.so* || echo "libGL.so* not found..."

# Copy in the built dependencies
COPY --from=build-image ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

RUN curl -Lo /usr/local/bin/aws-lambda-rie ${RIE}
RUN chmod +x /usr/local/bin/aws-lambda-rie

COPY ./scripts/lambda-entrypoint.sh /lambda-entrypoint.sh
RUN chmod +x /lambda-entrypoint.sh
RUN ls -l /lambda-entrypoint.sh

ENTRYPOINT  ["/lambda-entrypoint.sh"]