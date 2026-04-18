from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from core.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard.dashboard'))

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
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
