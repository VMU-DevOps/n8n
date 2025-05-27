from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect
import os
import csv
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter
import base64
import io
import requests

app = Flask(__name__)
EXPORT_FOLDER = "export"
LABEL_FILE = os.path.join(EXPORT_FOLDER, "labels.csv")
os.makedirs(EXPORT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/edit-labels")
def edit_labels():
    rows_html = ""
    if os.path.exists(LABEL_FILE):
        with open(LABEL_FILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                img_path = f"/download/{row['filename']}"
                rows_html += f'''
                <tr>
                    <td><img src="{img_path}"></td>
                    <td>{row['filename']}<input type="hidden" name="filename" value="{row['filename']}"></td>
                    <td>{row['text']}</td>
                    <td><input name="text" value="{row['text']}" maxlength="8"></td>
                </tr>
                '''
    with open("static/edit.html") as template:
        return render_template_string(template.read(), rows=rows_html)

@app.route("/update-labels", methods=["POST"])
def update_labels():
    filenames = request.form.getlist("filename")
    texts = request.form.getlist("text")
    with open(LABEL_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "text"])
        for f, t in zip(filenames, texts):
            writer.writerow([f, t])
    return redirect("/edit-labels")

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(EXPORT_FOLDER, filename, as_attachment=False)

@app.route("/captcha")
def get_captcha():
    from playwright.sync_api import sync_playwright
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

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}_processed.png"
        filepath = os.path.join(EXPORT_FOLDER, filename)
        image.save(filepath)

        ocr_response = requests.post("http://ocr-service-easyocr:6000/ocr", json={"image_base64": processed_base64})
        ocr_code = ocr_response.json().get("captcha_code", "")

        with open(LABEL_FILE, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if os.stat(LABEL_FILE).st_size == 0:
                writer.writerow(["filename", "text"])
            writer.writerow([filename, ocr_code])

        return jsonify({
            "original_image": original_base64,
            "image": processed_base64,
            "captcha_code": ocr_code,
            "screenshot": full_base64
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
