from flask import Blueprint, render_template
from core.db import get_db
from routes.utils import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    stats = {}
    for key, table in [
        ('patients', 'patients'), ('doctors', 'doctors'),
        ('appointments', 'appointments'), ('beds', 'beds'),
        ('students', 'students'), ('faculty', 'faculty'),
        ('courses', 'courses'), ('fees', 'fees'),
    ]:
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
        result = cursor.fetchone()
        stats[key] = result['total'] if result else 0
        
    cursor.close()
    return render_template('dashboard.html', stats=stats)
