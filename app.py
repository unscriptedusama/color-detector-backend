
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)  # Allow requests from your Netlify site

def detect_color_from_base64(img_data: str):
    # Expect data URL like "data:image/jpeg;base64,....."
    if "," in img_data:
        img_data = img_data.split(",")[1]

    try:
        img_bytes = base64.b64decode(img_data)
    except Exception:
        raise ValueError("Invalid base64 image data")

    npimg = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode image")

    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2
    r = 40  # sampling circle radius

    mask = np.zeros(frame.shape[:2], dtype="uint8")
    cv2.circle(mask, (cx, cy), r, 255, -1)

    mean = cv2.mean(frame, mask=mask)[:3]  # BGR
    b, g, r_ = [int(x) for x in mean]

    hex_code = "#{:02x}{:02x}{:02x}".format(r_, g, b)
    rgb_tuple = f"({r_},{g},{b})"
    return hex_code, rgb_tuple

@app.route("/", methods=["GET"])
def home():
    return "Backend is running"

@app.route("/detect", methods=["POST"])
def detect():
    try:
        payload = request.get_json(force=True)
        if "image" not in payload:
            return jsonify({"error": "Missing 'image' field"}), 400
        hex_code, rgb = detect_color_from_base64(payload["image"])
        return jsonify({"hex": hex_code, "rgb": rgb})
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "detail": str(e)}), 500

if __name__ == "__main__":
    # Local development
    app.run(host="0.0.0.0", port=5000)
