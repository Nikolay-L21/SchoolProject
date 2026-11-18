import os

import cv2

detector = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(
    BASE_DIR,
    "models",
    "face_detection_yunet_2023mar.onnx"
)
def detect_faces(img):
    height, width, _ = img.shape
    dtct = cv2.FaceDetectorYN.create(
        model= model_path,
        config="",
        input_size=(width, height),
        score_threshold=0.6,
        nms_threshold=0.3
    )
    _, faces = dtct.detect(img)
    return faces