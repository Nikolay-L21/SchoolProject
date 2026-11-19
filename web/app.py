import os
import sys
from datetime import date
from  web.services import attendance
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
from web.components.video_processor import OptimizedVideoProcessor
from dbManagement import attendance_db, faces_dp

db = faces_dp.load()

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
st.title("Система проверки посещаемости")
classes = sorted({
    student_class
    for student_class, vector in db.values()
})
if not db:
    st.warning("Сначала зарегистрируйте учеников.")
    st.stop()
if "attendance_session" not in st.session_state:
    st.session_state.attendance_session = None
if st.session_state.attendance_session is None:
    st.subheader("Новое занятие")
    lesson_date = st.date_input(
        "Дата занятия",
        value=date.today()
    )
    lesson_number = st.number_input(
        "Номер урока",
        value=1
    )
    lesson_name = st.text_input(
        "Предмет",
        value="Информатика"
    )
    group_name = st.selectbox(
        "Класс",
        options=classes
    )
    if st.button("Начать проверку посещаемости"):
        session_id = attendance.start_attendance(
            str(lesson_date),
            group_name,
            lesson_name,
            lesson_number
        )
        st.session_state.attendance_session = session_id
        st.session_state.lesson_date = str(lesson_date)
        st.session_state.group_name = group_name
        st.session_state.lesson_name = lesson_name
        st.session_state.lesson_number = lesson_number
        st.rerun()
else:

    session_id = st.session_state.attendance_session
    lesson_date = st.session_state.lesson_date
    group_name = st.session_state.group_name
    lesson_name = st.session_state.lesson_name
    lesson_number = st.session_state.lesson_number
    st.subheader("Проверка посещаемости")
    st.info(
        "Камера расположена над дверью. "
        "Ученик будет отмечен автоматически после распознавания."
    )
    students = [
        name
        for name, (student_class, vector) in db.items()
        if student_class == group_name
    ]
    ctx = webrtc_streamer(
        key=f"attendance-{session_id}",
        video_processor_factory=lambda: OptimizedVideoProcessor(db, group_name),
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
    @st.fragment(run_every=1)
    def attendance_panel():
        processor = ctx.video_processor
        if processor is not None:
            seen_names = processor.get_seen_names()
            attendance.register_detected_students(session_id, seen_names)
        col1, col2 = st.columns(2)
        present, absent= attendance.get_status(lesson_date, lesson_number,group_name,lesson_name,students)
        col1.metric(
            "Присутствуют",
            len(present)
        )
        col2.metric(
            "Ещё не обнаружены",
            len(absent)
        )
        st.write("Список учеников")
        for student in students:
            if student in present:
                st.success(f"✓ {student} - Присутствует")
            else:
                st.warning(f"○ {student} - Ещё не обнаружен")
        st.divider()
        if st.button("Завершить проверку", type="primary"):
            attendance.finish_attendance(session_id, students)
            st.session_state.attendance_session = None
            st.rerun()
    attendance_panel()

