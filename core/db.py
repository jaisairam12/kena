import sqlite3
import os
from flask import g, current_app

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apexcare.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row   # dict-like rows
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
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
