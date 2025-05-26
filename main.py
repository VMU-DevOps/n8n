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

        image = Image.open(io.BytesIO(captcha_bytes))
        code = pytesseract.image_to_string(image).strip()

        img_base64 = base64.b64encode(captcha_bytes).decode("utf-8")
        full_base64 = base64.b64encode(full_bytes).decode("utf-8")

        return jsonify({
            "image": img_base64,
            "captcha_code": code,
            "screenshot": full_base64
        })

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
        page.mouse.click(100, 100)
        page.wait_for_timeout(1000)
        login_button = page.query_selector("text=Đăng nhập")
        if login_button:
            login_button.click()
        page.wait_for_timeout(2000)

        page.fill("input[placeholder='Tên đăng nhập']", username)
        page.fill("input[placeholder='Mật khẩu']", password)
        page.fill("input[placeholder='Nhập mã captcha']", captcha)
        page.click("button:has-text('Đăng nhập')")
        page.wait_for_timeout(5000)
        content = page.content()
        if "Đăng xuất" in content:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "fail", "html": content})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
