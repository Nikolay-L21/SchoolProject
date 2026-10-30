import cv2
from detector import detect_faces
from recognizer import get_face_vector, compare_faces
from database import *

path = "C:\\Users\\nilaz\\Downloads\\Telegram Desktop\\photo_2026-10-30_10-51-08.jpg"
update("faces_db")
db = load()
faces = detect_faces(path)
img = cv2.imread(path)
for face in faces:
    x, y, w, h = map(int, face[:4])
    vector = get_face_vector(face, path)
    name = "Unknown"
    max_similarity = -1.0
    for db_name, db_vector in db.items():
        similarity = compare_faces(vector, db_vector)
        if similarity > 0.36 and similarity > max_similarity:
            max_similarity = similarity
            name = db_name
    color = (0, 255, 0)
    if (name == "Unknown"):
        color = (0, 0, 255)
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    cv2.putText(img, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
cv2.imshow("Found Faces", img)
cv2.waitKey(0)
cv2.destroyAllWindows()