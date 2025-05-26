from flask import Flask, request, jsonify, send_from_directory
import os
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import base64
import io

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/captcha")
def get_captcha():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://hoadondientu.gdt.gov.vn/")
        page.wait_for_selector("img#captchaImage")
        captcha_element = page.query_selector("img#captchaImage")
        captcha_bytes = captcha_element.screenshot()
        image = Image.open(io.BytesIO(captcha_bytes))
        code = pytesseract.image_to_string(image).strip()
        img_base64 = base64.b64encode(captcha_bytes).decode("utf-8")
        return jsonify({"image": img_base64, "captcha_code": code})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    captcha = data["captcha"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://hoadondientu.gdt.gov.vn/")
        page.fill("#username", username)
        page.fill("#password", password)
        page.fill("#captcha", captcha)
        page.click("#submit")
        page.wait_for_timeout(5000)
        content = page.content()
        if "Đăng xuất" in content:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "fail", "html": content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
