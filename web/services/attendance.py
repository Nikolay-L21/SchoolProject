from dbManagement import attendance_db


def start_attendance(lesson_date, group_name, lesson_name, lesson_number):
    return attendance_db.create_attendance_session(
        str(lesson_date),
        group_name,
        lesson_name,
        lesson_number
    )
def register_detected_students(session_id, detected_names):
    for name in detected_names:
        attendance_db.mark_present(session_id, name)
def get_status(lesson_date, lesson_number,group_name,lesson_name,students):
    records = attendance_db.get_attendance()
    present = [
        row[4] for row in records
        if row[0] == str(lesson_date)
           and row[2] == group_name
           and row[3] == lesson_name
           and row[5] == "Присутствует"
           and row[1] == lesson_number
    ]
    absent = set(students) - set(present)
    return present, absent
def finish_attendance(session_id, students):
    attendance_db.finalize_attendance(session_id, students)