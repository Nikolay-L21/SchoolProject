import cv2
def detect_faces(path):
    img = cv2.imread(path)
    height, width, _ = img.shape
    dtct = cv2.FaceDetectorYN.create(
        model="face_detection_yunet_2023mar.onnx",
        config="",
        input_size=(width, height),
        score_threshold=0.6,
        nms_threshold=0.3
    )
    _, faces = dtct.detect(img)
    return faces