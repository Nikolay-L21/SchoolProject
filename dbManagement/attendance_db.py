import sqlite3
def get_connection():
    return sqlite3.connect("../attendance.db")

def init_attendance():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_date TEXT NOT NULL,
                lesson_number INTEGER NOT NULL,
                group_name TEXT NOT NULL,
                lesson_name TEXT NOT NULL,
                UNIQUE(lesson_date, lesson_number, group_name, lesson_name)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                status TEXT NOT NULL,
                marked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, student_name)
            )
        """)
def create_attendance_session(lesson_date, group_name, lesson_name, lesson_number):
    init_attendance()

    with get_connection() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO attendance_sessions
            (lesson_date, group_name, lesson_name, lesson_number)
            VALUES (?, ?, ?, ?)
        """, (lesson_date, group_name, lesson_name, lesson_number))

        row = connection.execute("""
            SELECT id FROM attendance_sessions
            WHERE lesson_date = ?
            AND group_name = ?
            AND lesson_name = ?
            AND lesson_number = ?
        """, (lesson_date, group_name, lesson_name, lesson_number)).fetchone()

        return row[0]


def mark_present(session_id, student_name):
    init_attendance()

    with get_connection() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO attendance_records
            (session_id, student_name, status)
            VALUES (?, ?, 'Присутствует')
        """, (session_id, student_name))


def finalize_attendance(session_id, students):
    init_attendance()

    with get_connection() as connection:
        for student in students:
            connection.execute("""
                INSERT OR IGNORE INTO attendance_records
                (session_id, student_name, status)
                VALUES (?, ?, 'Отсутствует')
            """, (session_id, student))


def get_attendance():
    init_attendance()

    with get_connection() as connection:
        cursor = connection.execute("""
            SELECT
                s.lesson_date,
                s.lesson_number,
                s.group_name,
                s.lesson_name,
                r.student_name,
                r.status,
                r.marked_at
            FROM attendance_records r
            JOIN attendance_sessions s
                ON r.session_id = s.id
            ORDER BY s.lesson_date DESC
        """)

        return cursor.fetchall()
