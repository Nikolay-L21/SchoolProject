import os
import sqlite3

import cv2

from detector import detect_faces
from recognizer import get_face_vector


def get_connection():
    return sqlite3.connect("faces.db")

def init():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT EXISTS UNIQUE,
            vector BLOB NOT EXISTS
        )
        ''')
        connection.commit()

def update(db_images_path="faces_db"):
    init()
    files = os.listdir(db_images_path)
    with get_connection() as connection:
        cursor = connection.cursor()
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(db_images_path, file)
                name = os.path.splitext(file)[0]
                faces = detect_faces(img_path)
                if faces is not None and len(faces) == 1:
                    vector = get_face_vector(faces, img_path)
                    vector_blob = KK.tobytes()
                    try:
                        cursor.execute("""
                                                INSERT OR REPLACE INTO known_faces (name, vector)
                                                VALUES (?, ?)
                                                """, (name, vector_blob))
                    except sqlite3.Error as e:
                        print(f"Ошибка SQL при записи {name}: {e}")
                else:
                    print("INVALID IMAGE")
                connection.commit()

