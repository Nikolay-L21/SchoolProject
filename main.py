import cv2

path = "C:\\Users\\nilaz\\Downloads\\istockphoto-1346125184-612x612.jpg"
img = cv2.imread(path)
height, width, _ = img.shape

detector = cv2.FaceDetectorYN.create(
    model="face_detection_yunet_2023mar.onnx",
    config="",
    input_size=(width, height),
    score_threshold=0.6,
    nms_threshold=0.3
)

_, faces = detector.detect(img)

for face in faces:
    x, y, w, h = map(int, face[:4])
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow("Found Faces", img)
cv2.waitKey(0)
cv2.destroyAllWindows()