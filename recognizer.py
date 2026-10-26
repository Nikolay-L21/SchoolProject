import cv2
model_path = "face_recognition_sface_2021dec.onnx"
recognizer = cv2.FaceRecognizerSF.create(model_path, "")
def get_face_vector(face_data, img_path):
    img = cv2.imread(img_path)
    aligned_face = recognizer.alignCrop(img, face_data)
    vector = recognizer.feature(aligned_face)
    return vector