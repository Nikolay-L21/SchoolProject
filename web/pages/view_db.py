import os
import sys
import streamlit as st

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

from dbManagement import faces_dp

st.title("База данных учеников")
st.divider()
db = faces_dp.load()
if db == {}:
    st.info("База данных пока пуста.")
else:
    col1, col2 = st.columns(2)
    col1.metric(
        "Всего учеников",
        len(db)
    )
    classes = set()
    for class_, _ in db.values():
        classes.add(class_)
    col2.metric(
        "Количество классов",
        len(classes)
    )
    classes.add("Все классы")
    st.divider()

    selected_class = st.selectbox(
        "Фильтр по классу",
        classes, placeholder= "Все классы"
    )
    students = []
    for name, items in db.items():
        if(selected_class == "Все классы"):
            students.append({"ФИО":name, "Класс":items[0]})
        else:
            if(selected_class == items[0]):
                students.append({"ФИО":name, "Класс":items[0]})
    st.divider()
    st.subheader("Список учеников")
    st.dataframe(
        students,
        use_container_width=True,
        hide_index=True
    )