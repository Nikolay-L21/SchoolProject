import streamlit as st
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
    elif class_name is None:
        st.error("Выберите класс")
    elif file is None:
        st.error("Загрузите фотографию")
    else:
        db = faces_dp.load()
        res = db.update(name, class_name, file)
        if(res[0] == 0):
            st.error(res[1])
        else:
            st.success(res[1])

