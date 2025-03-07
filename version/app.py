import webview
import cv2
import dlib
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageEnhance, ImageOps
import base64
import io
import numpy as np

app = Flask(__name__)

face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("./dat/shape_predictor_68_face_landmarks.dat")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        data = request.json
        image_data = data.get('image')
        brightness = float(data.get('brightness', 1.5))

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        img_bytes = base64.b64decode(image_data.split(",")[1])
        img_cv = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img_cv is None:
            return jsonify({'error': 'Invalid image data'}), 400

        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        current_brightness = np.mean(gray)
        print(f"Brillo promedio actual: {current_brightness}")
        
        faces = face_detector(gray)

        if len(faces) == 0:
            return jsonify({'error': 'No face detected'}), 400

        face = faces[0]
        landmarks = landmark_predictor(gray, face)

        left_eye = (landmarks.part(36).x, landmarks.part(36).y)
        right_eye = (landmarks.part(45).x, landmarks.part(45).y)
        chin = (landmarks.part(8).x, landmarks.part(8).y)
        forehead_y = landmarks.part(27).y - (chin[1] - landmarks.part(27).y) // 2
        forehead = (landmarks.part(27).x, max(0, forehead_y))
        

        x_center = (left_eye[0] + right_eye[0]) // 2
        y_center = (chin[1] + forehead[1]) // 2
        side_length = max(chin[1] - forehead[1], right_eye[0] - left_eye[0]) * 2

        x_start = max(0, x_center - side_length // 2)
        y_start = max(0, y_center - side_length // 2)
        x_end = min(img_cv.shape[1], x_start + side_length)
        y_end = min(img_cv.shape[0], y_start + side_length)

        # #pintar los angulos faciales
        # cv2.circle(img_cv, left_eye, 5, (0, 0, 255), -1)  # Ojo izquierdo (Rojo)
        # cv2.circle(img_cv, right_eye, 5, (0, 255, 0), -1)  # Ojo derecho (Verde)
        # cv2.circle(img_cv, chin, 5, (255, 0, 0), -1)  # Barbilla (Azul)
        # cv2.circle(img_cv, forehead, 5, (0, 255, 255), -1)  # Frente (Amarillo)
        # cv2.line(img_cv, left_eye, right_eye, (255, 255, 0), 2)  # Línea entre los ojos (Cyan)
        # cv2.line(img_cv, left_eye, chin, (255, 0, 255), 2)  # Línea ojo izquierdo - barbilla (Magenta)
        # cv2.line(img_cv, right_eye, chin, (255, 0, 255), 2)  # Línea ojo derecho - barbilla (Magenta)
        # cv2.line(img_cv, chin, forehead, (0, 255, 255), 2)  # Línea barbilla - frente (Amarillo)
        # cv2.rectangle(img_cv, (x_start, y_start), (x_end, y_end), (0, 255, 0), 3)  # Rectángulo verde
        
        cropped_pil = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

        cropped = img_cv[y_start:y_end, x_start:x_end]
        cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        cropped_pil = cropped_pil.resize((1200, 1200), Image.LANCZOS)
        cropped_pil = ImageOps.expand(cropped_pil, border=(0, 0, 0, 0), fill=cropped_pil.getpixel((0, 0)))

        enhancer = ImageEnhance.Brightness(cropped_pil)
        cropped_pil = enhancer.enhance(brightness)

        if current_brightness < 150:  
            print("--------Ajustando brillo porque la imagen es demasiado oscura.--------")
            enhancer = ImageEnhance.Brightness(cropped_pil)
            cropped_pil = enhancer.enhance(1.5)  
        elif current_brightness > 160:  
            print("--------Reduciendo brillo porque la imagen es demasiado brillante.--------")
            enhancer = ImageEnhance.Brightness(cropped_pil)
            cropped_pil = enhancer.enhance(0.8)  
        
        else:
            print("--------El brillo de la imagen está dentro de un rango aceptable.--------")

        buffered = io.BytesIO()
        cropped_pil.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({'processed_image': f"data:image/jpeg;base64,{img_base64}"})

    except Exception as e:
        return jsonify({'error': f'Error procesando image: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
    # from threading import Thread
    # thread = Thread(target=lambda: app.run(debug=True, port=5000, use_reloader=False))
    # thread.daemon = True
    # thread.start()

    # webview.create_window("Photos", "http://127.0.0.1:5000")
    # webview.start()
