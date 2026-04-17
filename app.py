from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'apexcare_erp_secret_xK9mN2pQ7vR'

# ── Database path ───────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'apexcare.db')


# ── Per-request DB connection ────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row   # dict-like rows
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# ── Bootstrap schema on first run ───────────────────────────
def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT NOT NULL UNIQUE,
                password   TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT OR IGNORE INTO users (username, password)
                VALUES ('admin', 'admin123');

            CREATE TABLE IF NOT EXISTS patients (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                age        INTEGER NOT NULL,
                disease    TEXT NOT NULL,
                contact    TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT NOT NULL,
                qualification  TEXT NOT NULL,
                specialization TEXT NOT NULL,
                experience     INTEGER NOT NULL,
                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id  INTEGER NOT NULL,
                date       TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS beds (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                bed_number TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS students (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                course     TEXT NOT NULL,
                year       INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS faculty (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                department TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS courses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                credits     INTEGER NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date       TEXT NOT NULL,
                status     TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS fees (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                amount     REAL NOT NULL,
                status     TEXT NOT NULL DEFAULT 'Unpaid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
        """)
        db.commit()


# ── Auth decorator ───────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


# ══════════════════════════════════════════════════════
# LOGIN / LOGOUT
# ══════════════════════════════════════════════════════
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Both fields are required.', 'danger')
            return render_template('login.html')

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = username
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ══════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    stats = {}
    for key, table in [
        ('patients', 'patients'), ('doctors', 'doctors'),
        ('appointments', 'appointments'), ('beds', 'beds'),
        ('students', 'students'), ('faculty', 'faculty'),
        ('courses', 'courses'), ('fees', 'fees'),
    ]:
        stats[key] = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return render_template('dashboard.html', stats=stats)


# ══════════════════════════════════════════════════════
# HOSPITAL – PATIENTS
# ══════════════════════════════════════════════════════
@app.route('/hospital/patients', methods=['GET', 'POST'])
@login_required
def patients():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        name    = request.form.get('name',    '').strip()
        age     = request.form.get('age',     '').strip()
        disease = request.form.get('disease', '').strip()
        contact = request.form.get('contact', '').strip()

        if not all([name, age, disease, contact]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO patients (name, age, disease, contact) VALUES (?, ?, ?, ?)",
                    (name, int(age), disease, contact)
                )
                db.commit()
                msg, msg_type = 'Patient added successfully!', 'success'
            except Exception as e:
                print(f"[PATIENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_patients = db.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    return render_template('hospital/patients.html', patients=all_patients, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# HOSPITAL – DOCTORS
# ══════════════════════════════════════════════════════
@app.route('/hospital/doctors', methods=['GET', 'POST'])
@login_required
def doctors():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        name           = request.form.get('name',           '').strip()
        qualification  = request.form.get('qualification',  '').strip()
        specialization = request.form.get('specialization', '').strip()
        experience     = request.form.get('experience',     '').strip()

        if not all([name, qualification, specialization, experience]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO doctors (name, qualification, specialization, experience) VALUES (?, ?, ?, ?)",
                    (name, qualification, specialization, int(experience))
                )
                db.commit()
                msg, msg_type = 'Doctor added successfully!', 'success'
            except Exception as e:
                print(f"[DOCTORS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_doctors = db.execute("SELECT * FROM doctors ORDER BY id DESC").fetchall()
    return render_template('hospital/doctors.html', doctors=all_doctors, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# HOSPITAL – APPOINTMENTS
# ══════════════════════════════════════════════════════
@app.route('/hospital/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        doctor_id  = request.form.get('doctor_id',  '').strip()
        date       = request.form.get('date',        '').strip()
        status     = request.form.get('status',      '').strip()

        if not all([patient_id, doctor_id, date, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO appointments (patient_id, doctor_id, date, status) VALUES (?, ?, ?, ?)",
                    (int(patient_id), int(doctor_id), date, status)
                )
                db.commit()
                msg, msg_type = 'Appointment booked successfully!', 'success'
            except Exception as e:
                print(f"[APPOINTMENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_patients = db.execute("SELECT id, name FROM patients ORDER BY name").fetchall()
    all_doctors  = db.execute("SELECT id, name FROM doctors ORDER BY name").fetchall()
    all_appointments = db.execute("""
        SELECT a.id, p.name AS patient_name, d.name AS doctor_name,
               a.date, a.status, a.created_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.id DESC
    """).fetchall()
    return render_template(
        'hospital/appointments.html',
        patients=all_patients, doctors=all_doctors,
        appointments=all_appointments, msg=msg, msg_type=msg_type
    )


# ══════════════════════════════════════════════════════
# HOSPITAL – BEDS
# ══════════════════════════════════════════════════════
@app.route('/hospital/beds', methods=['GET', 'POST'])
@login_required
def beds():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        bed_number = request.form.get('bed_number', '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([bed_number, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO beds (bed_number, status) VALUES (?, ?)",
                    (bed_number, status)
                )
                db.commit()
                msg, msg_type = 'Bed record added successfully!', 'success'
            except Exception as e:
                print(f"[BEDS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_beds = db.execute("SELECT * FROM beds ORDER BY id DESC").fetchall()
    return render_template('hospital/beds.html', beds=all_beds, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# UNIVERSITY – STUDENTS
# ══════════════════════════════════════════════════════
@app.route('/university/students', methods=['GET', 'POST'])
@login_required
def students():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        name   = request.form.get('name',   '').strip()
        course = request.form.get('course', '').strip()
        year   = request.form.get('year',   '').strip()

        if not all([name, course, year]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO students (name, course, year) VALUES (?, ?, ?)",
                    (name, course, int(year))
                )
                db.commit()
                msg, msg_type = 'Student registered successfully!', 'success'
            except Exception as e:
                print(f"[STUDENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_students = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return render_template('university/students.html', students=all_students, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# UNIVERSITY – FACULTY
# ══════════════════════════════════════════════════════
@app.route('/university/faculty', methods=['GET', 'POST'])
@login_required
def faculty():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        name       = request.form.get('name',       '').strip()
        department = request.form.get('department', '').strip()

        if not all([name, department]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO faculty (name, department) VALUES (?, ?)",
                    (name, department)
                )
                db.commit()
                msg, msg_type = 'Faculty member added successfully!', 'success'
            except Exception as e:
                print(f"[FACULTY ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_faculty = db.execute("SELECT * FROM faculty ORDER BY id DESC").fetchall()
    return render_template('university/faculty.html', faculty=all_faculty, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# UNIVERSITY – COURSES
# ══════════════════════════════════════════════════════
@app.route('/university/courses', methods=['GET', 'POST'])
@login_required
def courses():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        credits     = request.form.get('credits',     '').strip()

        if not all([course_name, credits]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO courses (course_name, credits) VALUES (?, ?)",
                    (course_name, int(credits))
                )
                db.commit()
                msg, msg_type = 'Course added successfully!', 'success'
            except Exception as e:
                print(f"[COURSES ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_courses = db.execute("SELECT * FROM courses ORDER BY id DESC").fetchall()
    return render_template('university/courses.html', courses=all_courses, msg=msg, msg_type=msg_type)


# ══════════════════════════════════════════════════════
# UNIVERSITY – ATTENDANCE
# ══════════════════════════════════════════════════════
@app.route('/university/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        date       = request.form.get('date',       '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([student_id, date, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                    (int(student_id), date, status)
                )
                db.commit()
                msg, msg_type = 'Attendance marked successfully!', 'success'
            except Exception as e:
                print(f"[ATTENDANCE ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    all_attendance = db.execute("""
        SELECT a.id, s.name AS student_name, a.date, a.status, a.created_at
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.id DESC
    """).fetchall()
    return render_template(
        'university/attendance.html',
        students=all_students, attendance=all_attendance,
        msg=msg, msg_type=msg_type
    )


# ══════════════════════════════════════════════════════
# UNIVERSITY – FEES
# ══════════════════════════════════════════════════════
@app.route('/university/fees', methods=['GET', 'POST'])
@login_required
def fees():
    msg, msg_type = None, None
    db = get_db()

    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        amount     = request.form.get('amount',     '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([student_id, amount, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                db.execute(
                    "INSERT INTO fees (student_id, amount, status) VALUES (?, ?, ?)",
                    (int(student_id), float(amount), status)
                )
                db.commit()
                msg, msg_type = 'Fee record saved successfully!', 'success'
            except Exception as e:
                print(f"[FEES ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    all_students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    all_fees = db.execute("""
        SELECT f.id, s.name AS student_name, f.amount, f.status, f.created_at
        FROM fees f
        JOIN students s ON f.student_id = s.id
        ORDER BY f.id DESC
    """).fetchall()
    return render_template(
        'university/fees.html',
        students=all_students, fees=all_fees,
        msg=msg, msg_type=msg_type
    )


# ──────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()            # Create tables + seed admin on first run
    app.run(debug=True)
