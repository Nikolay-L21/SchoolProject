import cv2
from detector import detect_faces
from recognizer import get_face_vector

path = "C:\\Users\\nilaz\\Downloads\\istockphoto-1346125184-612x612.jpg"
faces = detect_faces(path)
img = cv2.imread(path)
all_vectors = []
for face in faces:
    x, y, w, h = map(int, face[:4])
    vector = get_face_vector(face, path)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow("Found Faces", img)
cv2.waitKey(0)
cv2.destroyAllWindows()