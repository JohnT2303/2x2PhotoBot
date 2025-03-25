import cv2
import dlib
import base64
import io
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image, ImageEnhance, ImageStat

app = Flask(__name__)

try:
    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor("./dat/shape_predictor_68_face_landmarks.dat")
except Exception as e:
    print(f"Error cargando modelos de dlib: {e}")
    face_detector = None
    landmark_predictor = None


def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def auto_adjust_brightness_contrast_cv(image, target_brightness=130):
    # Convert to LAB color space for better color preservation
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to L channel for local contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    
    # Calculate current brightness
    current_brightness = np.mean(l)
    
    # Adjust brightness with smooth transition
    brightness_factor = target_brightness / current_brightness
    l = np.clip(l * brightness_factor, 0, 255).astype(np.uint8)
    
    # Merge channels back
    lab = cv2.merge((l, a, b))
    
    # Convert back to BGR
    adjusted = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # Apply subtle color correction
    adjusted = cv2.convertScaleAbs(adjusted, alpha=1.1, beta=0)
    
    return adjusted

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if not face_detector or not landmark_predictor:
            return jsonify({'error': 'Modelos de detección de rostros no cargados'}), 500

        if 'file' not in request.files:
            return jsonify({'error': 'No se detecto una imagen'}), 400

        file = request.files['file']
        
        try:
            image = Image.open(file.stream)
        except IOError:
            return jsonify({'error': 'Archivo inválido o no es una imagen'}), 400

        img_cv = np.array(image)
        if img_cv is None or img_cv.size == 0:
            return jsonify({'error': 'Error leyendo la imagen'}), 400

        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        faces = face_detector(gray)
        if len(faces) == 0:
            return jsonify({'error': 'No se detectaron caras'}), 400

        face = faces[0]
        landmarks = landmark_predictor(gray, face)

        left_eye = (landmarks.part(36).x, landmarks.part(36).y)
        right_eye = (landmarks.part(45).x, landmarks.part(45).y)
        
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))

        img_cv = rotate_image(img_cv, angle)

        chin = (landmarks.part(8).x, landmarks.part(8).y)
        forehead_y = landmarks.part(27).y - (chin[1] - landmarks.part(27).y) // 2
        forehead = (landmarks.part(27).x, max(0, forehead_y))
        
        x_center = (left_eye[0] + right_eye[0]) // 2
        y_center = (chin[1] + forehead[1]) // 2
        side_length = max(chin[1] - forehead[1], right_eye[0] - left_eye[0]) * 2

        x_start = max(0, x_center - side_length // 2)
        x_end = min(img_cv.shape[1], x_start + side_length)
        y_start = max(0, y_center - side_length // 2)
        y_end = min(img_cv.shape[0], y_start + side_length)

        if x_end <= x_start or y_end <= y_start:
            return jsonify({'error': 'Error al recortar la imagen, coordenadas inválidas'}), 400
        
        #pintar los angulos faciales
        # cv2.circle(img_cv, left_eye, 5, (0, 0, 255), -1)  # Ojo izquierdo (Rojo)
        # cv2.circle(img_cv, right_eye, 5, (0, 255, 0), -1)  # Ojo derecho (Verde)
        # cv2.circle(img_cv, chin, 5, (255, 0, 0), -1)  # Barbilla (Azul)
        # cv2.circle(img_cv, forehead, 5, (0, 255, 255), -1)  # Frente (Amarillo)
        # cv2.line(img_cv, left_eye, right_eye, (255, 255, 0), 2)  # Línea entre los ojos (Cyan)
        # cv2.line(img_cv, left_eye, chin, (255, 0, 255), 2)  # Línea ojo izquierdo - barbilla (Magenta)
        # cv2.line(img_cv, right_eye, chin, (255, 0, 255), 2)  # Línea ojo derecho - barbilla (Magenta)
        # cv2.line(img_cv, chin, forehead, (0, 255, 255), 2)  # Línea barbilla - frente (Amarillo)
        # cv2.rectangle(img_cv, (x_start, y_start), (x_end, y_end), (0, 255, 0), 3)  # Rectángulo verde

        cropped = img_cv[y_start:y_end, x_start:x_end]
        if cropped.size == 0:
            return jsonify({'error': 'Error al recortar la imagen'}), 400

        face_roi = gray[y_start:y_end, x_start:x_end]
        current_brightness = np.mean(face_roi)
        print(f"Brillo promedio actual: {current_brightness}")

        cropped_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        cropped_pil = cropped_pil.resize((1200, 1200), Image.LANCZOS)
        cropped = auto_adjust_brightness_contrast_cv(cropped)
        buffered = io.BytesIO()
        cropped_pil.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return jsonify({'processed_image': f"data:image/jpeg;base64,{img_base64}"})

    except Exception as e:
        print(f"Error procesando imagen: {str(e)}")
        return jsonify({'error': f'Error procesando imagen: {str(e)}'}), 500




if __name__ == '__main__':
    app.run(debug=True, port=5000)



