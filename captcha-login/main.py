from flask import Flask, request, jsonify, send_from_directory
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageFilter, ImageOps
import base64
import io
import requests
from datetime import datetime

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/captcha")
def get_captcha():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://hoadondientu.gdt.gov.vn/", timeout=60000)
        page.wait_for_timeout(3000)
        page.mouse.click(100, 100)
        page.wait_for_timeout(1000)
        login_button = page.query_selector("text=Đăng nhập")
        if login_button:
            login_button.click()
        page.wait_for_selector("div.ant-modal-content", timeout=5000)

        login_modal = page.query_selector("div.ant-modal-content")
        captcha_img = login_modal.query_selector("img[alt='captcha']")
        if not captcha_img:
            return jsonify({"error": "Không tìm thấy captcha trong modal"}), 500

        captcha_bytes = captcha_img.screenshot()
        full_bytes = page.screenshot(full_page=True)

        original_base64 = base64.b64encode(captcha_bytes).decode("utf-8")

        image = Image.open(io.BytesIO(captcha_bytes)).convert("L")
        image = ImageOps.invert(image)
        image = image.filter(ImageFilter.MedianFilter(size=3))
        image = image.point(lambda x: 0 if x < 128 else 255, '1')

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        processed_bytes = buffer.getvalue()
        processed_base64 = base64.b64encode(processed_bytes).decode("utf-8")
        full_base64 = base64.b64encode(full_bytes).decode("utf-8")

        # Export to local file for dataset
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        image.save(f"export/{ts}_processed.png")

        # EasyOCR
        easyocr_resp = requests.post("http://ocr-service-easyocr:6000/ocr", json={"image_base64": processed_base64})
        easy_text = easyocr_resp.json().get("captcha_code", "")

        # PaddleOCR
        paddle_resp = requests.post("http://ocr-service-paddleocr/predict/ocr_system", json={"images": [processed_base64]})
        paddle_result = paddle_resp.json()[0]["data"]
        paddle_text = " ".join([item[1][0] for item in paddle_result]) if paddle_result else ""

        return jsonify({
            "original_image": original_base64,
            "image": processed_base64,
            "captcha_easyocr": easy_text,
            "captcha_paddleocr": paddle_text,
            "screenshot": full_base64
        })

if __name__ == "__main__":
    os.makedirs("export", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
