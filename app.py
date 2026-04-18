import os
from flask import Flask
from core.db import close_db, init_db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'apexcare_erp_secret_xK9mN2pQ7vR'

    # Register teardown
    app.teardown_appcontext(close_db)

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.hospital import hospital_bp
    from routes.university import university_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(hospital_bp)
    app.register_blueprint(university_bp)

    return app

app = create_app()

if __name__ == '__main__':
    init_db(app)            # Create tables + seed admin on first run
    app.run(debug=True)
