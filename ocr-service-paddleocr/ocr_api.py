from flask import Flask, request, jsonify
import base64
import io
from PIL import Image
from paddleocr import PaddleOCR

app = Flask(__name__)
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    data = request.json
    img_data = data.get("image_base64", "")
    if not img_data:
        return jsonify({"error": "No image_base64 provided"}), 400

    try:
        image = Image.open(io.BytesIO(base64.b64decode(img_data))).convert("RGB")
        result = ocr.ocr(image, cls=True)
        text = " ".join([line[1][0] for line in result[0]]).strip()
        return jsonify({"captcha_code": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
