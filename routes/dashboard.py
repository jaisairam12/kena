from flask import Blueprint, render_template
from core.db import get_db
from routes.utils import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
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
