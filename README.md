# FotoSedIt - Professional Photo Enhancement API

A powerful Flask-based API service that automatically enhances portrait photos using advanced computer vision techniques. This project focuses on professional-grade photo processing with emphasis on facial features and natural-looking enhancements.

## 🌟 Features

- **Automatic Face Detection and Alignment**: Uses dlib's face detection to identify and align faces in photos
- **Smart Cropping**: Automatically crops photos to focus on the face while maintaining proper composition
- **Advanced Image Enhancement**:
  - Intelligent brightness and contrast adjustment
  - Local contrast enhancement using CLAHE
  - Color preservation in LAB color space
  - Natural skin tone preservation
- **High-Resolution Output**: Processes images to 1200x1200 pixels while maintaining quality
- **RESTful API**: Easy to integrate with any web application

## 🛠️ Technical Stack

- Python 3.x
- Flask
- OpenCV (cv2)
- dlib
- PIL (Python Imaging Library)
- NumPy

## 📋 Prerequisites

- Python 3.x installed
- dlib shape predictor file (`shape_predictor_68_face_landmarks.dat`)
- Required Python packages (see requirements.txt)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/JohnT2303/2x2PhotoBot.git
cd fotosedit
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download the dlib shape predictor file:
```bash
# Create dat directory if it doesn't exist
mkdir dat
# Download the shape predictor file to the dat directory
# You can download it from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
```

## 🚀 Usage

1. Start the Flask server:
```bash
python api.process.py
```

2. The API will be available at `http://localhost:5000`

3. Send a POST request to `/process_image` with an image file:
```python
import requests

url = 'http://localhost:5000/process_image'
files = {'file': open('path_to_your_image.jpg', 'rb')}
response = requests.post(url, files=files)
```

## 📝 API Endpoints

### POST /process_image

Processes an uploaded image and returns the enhanced version.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Image file in 'file' field

**Response:**
- Content-Type: application/json
- Body: 
  ```json
  {
    "processed_image": "data:image/jpeg;base64,..."
  }
  ```

## 🔍 How It Works

1. **Face Detection**: Uses dlib's face detector to locate faces in the image
2. **Alignment**: Detects facial landmarks and aligns the face horizontally
3. **Smart Cropping**: Calculates optimal crop area based on facial features
4. **Enhancement**:
   - Converts image to LAB color space for better color preservation
   - Applies CLAHE for local contrast enhancement
   - Adjusts brightness while preserving skin tones
   - Applies subtle color correction
5. **Output**: Returns the processed image in base64 format

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

John Torres
- GitHub: [[Your GitHub Profile]](https://github.com/JohnT2303/)


## 🙏 Acknowledgments

- dlib library and its contributors
- OpenCV community
- Flask framework 
