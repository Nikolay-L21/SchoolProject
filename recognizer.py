import cv2
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "models/face_recognition_sface_2021dec.onnx")
recognizer = cv2.FaceRecognizerSF.create(model_path, "")
def get_face_vector(face_data, img):
    aligned_face = recognizer.alignCrop(img, face_data)
    vector = recognizer.feature(aligned_face)
    return vector
def compare_faces(v1, v2):
    return recognizer.match(v1, v2, cv2.FaceRecognizerSF_FR_COSINE)