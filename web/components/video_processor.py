import threading
from datetime import time

import av
import cv2
from streamlit_webrtc import VideoProcessorBase
from detector import detect_faces
from recognizer import get_face_vector, compare_faces


class OptimizedVideoProcessor(VideoProcessorBase):
    def __init__(self, faces_database):
        self.db = faces_database
        self.last_detection_time = 0.0
        self.detection_interval = 0.15
        self.last_faces = []
        self.seen_names = set()
        self.target_similarity = 0.36
        self.hit_counts = {}
        self.last_hit_time = {}
        self.lock = threading.Lock()
        self.required_hits = 2
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24").copy()
        current_time = time.monotonic()
        if  current_time - self.last_detection_time >= self.detection_interval:
            self.last_detection_time = current_time
            self.process_faces(image)
        self.draw(image)
        return image.av.VideoFrame.from_ndarray(image, format="bgr24")

    def process_faces(self, image):
        faces = detect_faces(image)
        detected_faces = []
        if faces is not None and len(faces) > 0:
            for face in faces:
                x, y, w, h = map(int, face[:4])
                vector = get_face_vector(face, image)
                name = self.recognize(vector)
                detected_faces.append((x, y, w, h, name))
                if name != "Unknown":
                    self._register_hit(name) #*
        self.last_faces = detected_faces
    def recognize(self, vector):
        name = "Unknown"
        max_similarity = -1.0
        for db_name, db_vector in self.db.items():
            similarity = compare_faces(vector, db_vector)
            if similarity > self.target_similarity and similarity > max_similarity:
                max_similarity = similarity
                name = db_name
        return name
    def _register_hit(self, name):
        if name != "Unknown":
            with self.lock:
                current_time = time.monotonic()
                if current_time - self.last_hit_time.get(name, 0) > 3:
                    self.hit_counts[name] = 0
                self.hit_counts[name] = self.hit_counts.get(name, 0) + 1
                self.last_hit_time[name] = current_time
                if self.hit_counts[name] >= self.required_hits:
                    self.seen_names.add(name)
    def get_seen_names(self):
        with self.lock:
            return set(self.seen_names)
    def draw(self, image):
        for (x, y, w, h, name) in self.last_faces:
            if name != "Unknown":
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        new_frame = av.VideoFrame.from_ndarray(image, format="bgr24")
        new_frame.pts = image.pts
        new_frame.time_base = image.time_base
        return new_frame
