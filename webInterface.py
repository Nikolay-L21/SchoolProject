import streamlit as st
import database
import numpy as np
import cv2
st.write("test")
name = st.text_input("Введите имя")
file = st.file_uploader("Загрузите изображение человека",
                        type=["jpeg", "jpg", "png"])
if (st.button("Загрузить изображение и обновить базу данных")):
    if (file is not None):
        file_bytes = np.frombuffer(file.read(), np.uint8)
        opencv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        database.update(name, opencv_image)
        st.write("Успех!")
    else:
        st.write("Ошибка загрузки")
