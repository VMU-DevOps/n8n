from flask import Flask, request, jsonify, send_from_directory
import os
from playwright.sync_api import sync_playwright
from PIL import Image
import base64
import io
import requests

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
        page.wait_for_timeout(3000)

        captcha_img = page.query_selector("img[alt='captcha']")
        if not captcha_img:
            return jsonify({"error": "Không tìm thấy ảnh captcha"}), 500

        captcha_bytes = captcha_img.screenshot()
        full_bytes = page.screenshot(full_page=True)
        img_base64 = base64.b64encode(captcha_bytes).decode("utf-8")
        full_base64 = base64.b64encode(full_bytes).decode("utf-8")

        # Gửi ảnh sang OCR API
        ocr_response = requests.post("http://ocr-service:6000/ocr", json={"image_base64": img_base64})
        ocr_code = ocr_response.json().get("captcha_code", "")

        return jsonify({
            "image": img_base64,
            "captcha_code": ocr_code,
            "screenshot": full_base64
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
