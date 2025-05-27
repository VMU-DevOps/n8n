from flask import Flask, request, jsonify
import base64
import io
from PIL import Image
import easyocr

app = Flask(__name__)
reader = easyocr.Reader(['en'], gpu=False)

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    img_data = data.get("image_base64", "")
    if not img_data:
        return jsonify({"error": "No image_base64 provided"}), 400

    try:
        image = Image.open(io.BytesIO(base64.b64decode(img_data))).convert("RGB")
        result = reader.readtext(image)
        text = " ".join([x[1] for x in result]).strip()
        return jsonify({"captcha_code": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
