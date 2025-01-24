import webview
import cv2
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageEnhance
import base64
import io
import numpy as np

app = Flask(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_data = data['image']
    brightness = float(data['brightness'])

    img_bytes = base64.b64decode(image_data.split(",")[1])
    img = Image.open(io.BytesIO(img_bytes))

    nparr = np.frombuffer(img_bytes, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    if len(faces) == 0:
        print("No faces detected. Proceeding with original image.")
        # Si no se detectan rostros, utilizamos toda la imagen
        x, y, w, h = 0, 0, img_cv.shape[1], img_cv.shape[0]
    else:
        x, y, w, h = faces[0]

        side_length = max(w, h)
        x_center, y_center = x + w // 2, y + h // 2
        x_start = max(0, x_center - side_length)
        y_start = max(0, y_center - side_length)
        x_end = min(img_cv.shape[1], x_center + side_length)
        y_end = min(img_cv.shape[0], y_center + side_length)

        cropped = img_cv[y_start:y_end, x_start:x_end]

        img_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))

    # Ajustamos el brillo de la imagen (recortada o original)
    enhancer = ImageEnhance.Brightness(img_pil)
    img_pil = enhancer.enhance(brightness)

    # Convertimos la imagen procesada a formato JPEG
    buffered = io.BytesIO()
    img_pil.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return jsonify({'processed_image': f"data:image/jpeg;base64,{img_base64}"})


if __name__ == '__main__':
    from threading import Thread
    thread = Thread(target=lambda: app.run(debug=True, port=5000, use_reloader=False))
    thread.daemon = True
    thread.start()

    # Crea la ventana con pywebview
    webview.create_window("Photo Processor", "http://127.0.0.1:5000")
    webview.start()
