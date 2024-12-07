FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-pyqt5 \
    python3-pyqt5.qtopengl \
    && apt-get clean

WORKDIR /app

COPY image_annotator.py /app/

RUN pip3 install numpy opencv-pythonk
