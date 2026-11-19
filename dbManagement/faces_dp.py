import os
import sqlite3
import numpy as np
from detector import detect_faces
from recognizer import get_face_vector

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(BASE_DIR, "faces.db")
def get_connection():
    return sqlite3.connect(DB_PATH)

def init():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS known_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            class_name TEXT NOT NULL,
            vector BLOB NOT NULL
        )
        ''')
        connection.commit()


def update(name, class_name, img):
    init()
    with get_connection() as connection:
        cursor = connection.cursor()
        faces = detect_faces(img)
        if faces is not None and len(faces) == 1:
            vector = get_face_vector(faces[0], img)
            vector_blop = vector.tobytes()
            try:
                cursor.execute("""
                                        INSERT OR REPLACE INTO known_faces (name, class_name, vector)
                                        VALUES (?, ?, ?)
                                        """, (name,class_name, vector_blop))
                connection.commit()
            except sqlite3.Error as e:
                return [0, (f"Ошибка записи SQL: {e}")]
            else:
                return [1,"Успех"]
        else:
            return [0, "Некорректное изображение"]


def load():
    known_faces = {}
    init()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name, class_name, vector FROM known_faces")
        rows = cursor.fetchall()
        for name, class_name, vector_blop in rows:
            vector = np.frombuffer(vector_blop, dtype=np.float32).reshape(1, 128)
            known_faces[name] = [class_name, vector]
    return known_faces