FROM python:3.10-slim

RUN apt-get update && apt-get install -y tesseract-ocr &&     pip install flask pillow pytesseract

WORKDIR /app
COPY ocr_api.py .

CMD ["python", "ocr_api.py"]
