from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated
