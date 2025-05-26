FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

RUN apt-get update && apt-get install -y tesseract-ocr

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN playwright install

CMD ["python", "main.py"]
