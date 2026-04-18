from flask import Blueprint, render_template, request
from core.db import get_db
from routes.utils import login_required

university_bp = Blueprint('university', __name__, url_prefix='/university')

@university_bp.route('/students', methods=['GET', 'POST'])
@login_required
def students():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name   = request.form.get('name',   '').strip()
        course = request.form.get('course', '').strip()
        year   = request.form.get('year',   '').strip()

        if not all([name, course, year]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO students (name, course, year) VALUES (%s, %s, %s)",
                    (name, course, int(year))
                )
                db.commit()
                msg, msg_type = 'Student registered successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[STUDENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    all_students = cursor.fetchall()
    cursor.close()
    return render_template('university/students.html', students=all_students, msg=msg, msg_type=msg_type)


@university_bp.route('/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name       = request.form.get('name',       '').strip()
        department = request.form.get('department', '').strip()

        if not all([name, department]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO faculty (name, department) VALUES (%s, %s)",
                    (name, department)
                )
                db.commit()
                msg, msg_type = 'Faculty member added successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[FACULTY ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM faculty ORDER BY id DESC")
    all_faculty = cursor.fetchall()
    cursor.close()
    return render_template('university/faculty.html', faculty=all_faculty, msg=msg, msg_type=msg_type)


@university_bp.route('/courses', methods=['GET', 'POST'])
@login_required
def courses():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        credits     = request.form.get('credits',     '').strip()

        if not all([course_name, credits]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO courses (course_name, credits) VALUES (%s, %s)",
                    (course_name, int(credits))
                )
                db.commit()
                msg, msg_type = 'Course added successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[COURSES ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM courses ORDER BY id DESC")
    all_courses = cursor.fetchall()
    cursor.close()
    return render_template('university/courses.html', courses=all_courses, msg=msg, msg_type=msg_type)


@university_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        date       = request.form.get('date',       '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([student_id, date, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                    (int(student_id), date, status)
                )
                db.commit()
                msg, msg_type = 'Attendance marked successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[ATTENDANCE ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT id, name FROM students ORDER BY name")
    all_students = cursor.fetchall()
    
    cursor.execute("""
        SELECT a.id, s.name AS student_name, a.date, a.status, a.created_at
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.id DESC
    """)
    all_attendance = cursor.fetchall()
    cursor.close()
    
    return render_template(
        'university/attendance.html',
        students=all_students, attendance=all_attendance,
        msg=msg, msg_type=msg_type
    )


@university_bp.route('/fees', methods=['GET', 'POST'])
@login_required
def fees():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        amount     = request.form.get('amount',     '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([student_id, amount, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO fees (student_id, amount, status) VALUES (%s, %s, %s)",
                    (int(student_id), float(amount), status)
                )
                db.commit()
                msg, msg_type = 'Fee record saved successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[FEES ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT id, name FROM students ORDER BY name")
    all_students = cursor.fetchall()
    
    cursor.execute("""
        SELECT f.id, s.name AS student_name, f.amount, f.status, f.created_at
        FROM fees f
        JOIN students s ON f.student_id = s.id
        ORDER BY f.id DESC
    """)
    all_fees = cursor.fetchall()
    cursor.close()
    
    return render_template(
        'university/fees.html',
        students=all_students, fees=all_fees,
        msg=msg, msg_type=msg_type
    )
