import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
path = "C:\\Users\\nilaz\\Downloads\\istockphoto-1346125184-612x612.jpg"
img = cv2.imread(path, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(
    img, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
)

for x, y, w, h in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow("Found Faces", img)
cv2.waitKey(0)
cv2.destroyAllWindows()