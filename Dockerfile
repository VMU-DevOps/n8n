
FROM mcr.microsoft.com/playwright:v1.43.1-jammy

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y tesseract-ocr python3-pip && \
    pip3 install pytesseract pillow && \
    npm install

CMD ["node", "login_gdt.js"]
