import os
import sys
import threading
import time
from datetime import date

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detector import detect_faces
from recognizer import get_face_vector, compare_faces
import database
db = database.load()
class OptimizedVideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.last_detection_time = 0.0
        self.detection_interval = 0.15
        self.last_faces = []
        self.seen_names = set()
        self.hit_counts = {}
        self.last_hit_time = {}
        self.lock = threading.Lock()
        self.required_hits = 2
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        opencv_image = frame.to_ndarray(format="bgr24").copy()
        current_time = time.monotonic()
        if  current_time - self.last_detection_time > self.detection_interval:
            self.last_detection_time = current_time
            faces = detect_faces(opencv_image)
            self.last_faces = []
            if faces is not None and len(faces) > 0:
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
                    self.last_faces.append((x, y, w, h, name))
                    if name != "Unknown":
                        with self.lock:
                            current_time = time.monotonic()
                            if current_time - self.last_hit_time.get(name, 0) > 3:
                                self.hit_counts[name] = 0
                            self.hit_counts[name] = self.hit_counts.get(name, 0) + 1
                            self.last_hit_time[name] = current_time
                            if self.hit_counts[name] >= self.required_hits:
                                self.seen_names.add(name)
        for (x, y, w, h, name) in self.last_faces:
            if name != "Unknown": color = (0, 255, 0)
            else: color = (0, 0, 255)
            cv2.rectangle(opencv_image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(opencv_image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        new_frame = av.VideoFrame.from_ndarray(opencv_image, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame
    def get_seen_names(self):
        with self.lock:
            return set(self.seen_names)

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
st.title("Система проверки посещаемости")
students = list(db.keys())
if not students:
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
    group_name = st.text_input(
        "Класс",
        value="10А"
    )

    if st.button("Начать проверку посещаемости"):
        session_id = database.create_attendance_session(str(lesson_date),
                                                        group_name, lesson_name, lesson_number)
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
    ctx = webrtc_streamer(
        key=f"attendance-{session_id}",
        video_processor_factory=OptimizedVideoProcessor,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
    @st.fragment(run_every=1)
    def attendance_panel():
        processor = ctx.video_processor
        if processor is not None:
            seen_names = processor.get_seen_names()
            for name in seen_names:
                database.mark_present(session_id, name)
        records = database.get_attendance()
        present = [
            row[4] for row in records
            if row[0] == str(lesson_date)
               and row[2] == group_name
               and row[3] == lesson_name
               and row[5] == "Присутствует"
               and row[1] == lesson_number
        ]
        absent = set(students) - set(present)
        col1, col2 = st.columns(2)
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
            database.finalize_attendance(session_id, students)
            st.session_state.attendance_session = None
            st.rerun()
    attendance_panel()

