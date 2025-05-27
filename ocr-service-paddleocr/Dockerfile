FROM python:3.10-slim

RUN apt-get update && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev

RUN pip install paddlepaddle==2.5.2 paddleocr flask

WORKDIR /app
COPY ocr_api.py .

CMD ["python", "ocr_api.py"]
