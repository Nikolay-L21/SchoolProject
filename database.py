import os
import sqlite3

import cv2
import numpy as np

from detector import detect_faces
from recognizer import get_face_vector


def get_connection():
    return sqlite3.connect("faces.db")

def init():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS known_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            vector BLOB NOT NULL
        )
        ''')
        connection.commit()

def update(name, img):
    init()
    with get_connection() as connection:
        cursor = connection.cursor()
        faces = detect_faces(img)
        if faces is not None and len(faces) == 1:
            vector = get_face_vector(faces, img)
            vector_blop = vector.tobytes()
            try:
                cursor.execute("""
                                        INSERT OR REPLACE INTO known_faces (name, vector)
                                        VALUES (?, ?)
                                        """, (name, vector_blop))
            except sqlite3.Error as e:
                print (f"Ошибка SQL при записи {name}: {e}")
        else:
            print("INVALID IMAGE")
        connection.commit()

def load():
    known_faces = {}
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name, vector FROM known_faces")
        rows = cursor.fetchall()
        for name, vector_blop in rows:
            vector = np.frombuffer(vector_blop, dtype=np.float32).reshape(1, 128)
            known_faces[name] = vector
    return known_faces