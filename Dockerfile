FROM ghcr.io/osgeo/gdal:ubuntu-small-3.7.2

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./requirements_pip.txt /code/requirements_pip.txt

RUN apt update && apt install -y g++ make cmake unzip libcurl4-openssl-dev python3-pip

# avoid segment-geospatial exception caused by missing libGL.so.1 library
RUN apt install -y libgl1 curl
RUN ls -ld /usr/lib/x86_64-linux-gnu/libGL.so* || echo "libGL.so* not found..."

RUN which python
RUN python --version
RUN python -m pip install --no-cache-dir --upgrade -r /code/requirements_pip.txt
RUN python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN python -m pip install --no-cache-dir -r /code/requirements.txt

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

RUN curl -o ${HOME}/sam_vit_h_4b8939.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
RUN ls -l ${HOME}/
COPY --chown=user . $HOME/app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]