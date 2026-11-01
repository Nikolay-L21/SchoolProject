import streamlit as st
import numpy as np
import cv2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from recognizer import get_face_vector, compare_faces
from detector import detect_faces

st.write("test")

file = st.file_uploader("Загрузите изображение для распознавания",
                        type=["jpeg", "jpg", "png"])
if (st.button("Загрузить изображение")):
    if (file is not None):
        file_bytes = np.frombuffer(file.read(), np.uint8)
        db = database.load()
        opencv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        faces = detect_faces(opencv_image)
        for face in faces:
            x, y, w, h = map(int, face[:4])
            vector = get_face_vector(face, opencv_image)
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
            cv2.rectangle(opencv_image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(opencv_image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        st.image(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
    else:
        st.write("Ошибка загрузки")
