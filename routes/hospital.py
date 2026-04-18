from flask import Blueprint, render_template, request
from core.db import get_db
from routes.utils import login_required

hospital_bp = Blueprint('hospital', __name__, url_prefix='/hospital')

@hospital_bp.route('/patients', methods=['GET', 'POST'])
@login_required
def patients():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name    = request.form.get('name',    '').strip()
        age     = request.form.get('age',     '').strip()
        disease = request.form.get('disease', '').strip()
        contact = request.form.get('contact', '').strip()

        if not all([name, age, disease, contact]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO patients (name, age, disease, contact) VALUES (%s, %s, %s, %s)",
                    (name, int(age), disease, contact)
                )
                db.commit()
                msg, msg_type = 'Patient added successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[PATIENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    all_patients = cursor.fetchall()
    cursor.close()
    return render_template('hospital/patients.html', patients=all_patients, msg=msg, msg_type=msg_type)


@hospital_bp.route('/doctors', methods=['GET', 'POST'])
@login_required
def doctors():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        name           = request.form.get('name',           '').strip()
        qualification  = request.form.get('qualification',  '').strip()
        specialization = request.form.get('specialization', '').strip()
        experience     = request.form.get('experience',     '').strip()

        if not all([name, qualification, specialization, experience]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO doctors (name, qualification, specialization, experience) VALUES (%s, %s, %s, %s)",
                    (name, qualification, specialization, int(experience))
                )
                db.commit()
                msg, msg_type = 'Doctor added successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[DOCTORS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM doctors ORDER BY id DESC")
    all_doctors = cursor.fetchall()
    cursor.close()
    return render_template('hospital/doctors.html', doctors=all_doctors, msg=msg, msg_type=msg_type)


@hospital_bp.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        patient_id = request.form.get('patient_id', '').strip()
        doctor_id  = request.form.get('doctor_id',  '').strip()
        date       = request.form.get('date',        '').strip()
        status     = request.form.get('status',      '').strip()

        if not all([patient_id, doctor_id, date, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO appointments (patient_id, doctor_id, date, status) VALUES (%s, %s, %s, %s)",
                    (int(patient_id), int(doctor_id), date, status)
                )
                db.commit()
                msg, msg_type = 'Appointment booked successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[APPOINTMENTS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT id, name FROM patients ORDER BY name")
    all_patients = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM doctors ORDER BY name")
    all_doctors  = cursor.fetchall()
    
    cursor.execute("""
        SELECT a.id, p.name AS patient_name, d.name AS doctor_name,
               a.date, a.status, a.created_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.id DESC
    """)
    all_appointments = cursor.fetchall()
    cursor.close()
    
    return render_template(
        'hospital/appointments.html',
        patients=all_patients, doctors=all_doctors,
        appointments=all_appointments, msg=msg, msg_type=msg_type
    )


@hospital_bp.route('/beds', methods=['GET', 'POST'])
@login_required
def beds():
    msg, msg_type = None, None
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        bed_number = request.form.get('bed_number', '').strip()
        status     = request.form.get('status',     '').strip()

        if not all([bed_number, status]):
            msg, msg_type = 'All fields are required!', 'danger'
        else:
            try:
                cursor.execute(
                    "INSERT INTO beds (bed_number, status) VALUES (%s, %s)",
                    (bed_number, status)
                )
                db.commit()
                msg, msg_type = 'Bed record added successfully!', 'success'
            except Exception as e:
                db.rollback()
                print(f"[BEDS ERROR] {e}")
                msg, msg_type = f'Error: {e}', 'danger'

    cursor.execute("SELECT * FROM beds ORDER BY id DESC")
    all_beds = cursor.fetchall()
    cursor.close()
    return render_template('hospital/beds.html', beds=all_beds, msg=msg, msg_type=msg_type)
