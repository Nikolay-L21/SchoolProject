import os
import sys

import cv2
import numpy as np
import streamlit as st
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from dbManagement import faces_dp

st.title("Регистрация ученика")
st.divider()

st.subheader("Данные ученика")
name = st.text_input("Введите имя")
class_name = st.text_input("Выберите класс")
st.divider()

st.subheader("Фотография ученика")
file = st.file_uploader(
    "Загрузите фотографию",
    type=["jpg", "jpeg", "png"],
    help="Поддерживаются форматы JPG, JPEG и PNG"
)


if st.button(
    "Зарегистрировать ученика",
    type="primary",
    use_container_width=True):
    if not name.strip():
        st.error("Введите ФИО ученика")
    elif not class_name.strip():
        st.error("Выберите класс")
    elif file is None:
        st.error("Загрузите фотографию")
    else:
        file_bytes = np.frombuffer(file.getvalue(),np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            st.error("Не удалось декодировать изображение")
        else:
            res = faces_dp.update(name, class_name, img)
            if(res[0] == 0):
                st.error(res[1])
            else:
                st.success(res[1])

