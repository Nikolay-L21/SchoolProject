import os
import sys
import time

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
        for (x, y, w, h, name) in self.last_faces:
            if name != "Unknown": color = (0, 255, 0)
            else: color = (0, 0, 255)
            cv2.rectangle(opencv_image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(opencv_image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        new_frame = av.VideoFrame.from_ndarray(opencv_image, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)
webrtc_streamer(
    key="face-recognition-optimized",
    video_processor_factory=OptimizedVideoProcessor,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True
)