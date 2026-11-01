import cv2
def detect_faces(img):
    model_path = "face_detection_yunet_2023mar.onnx"
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