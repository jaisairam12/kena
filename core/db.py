import os
import sqlite3
import pymysql
import pymysql.cursors
from flask import g

class SQLiteCursorWrapper:
    """Wrapper that acts like a PyMySQL DictCursor but transparently executes SQLite queries."""
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        
    def execute(self, query, args=None):
        # 1. Migrate syntax tokens: MySQL `%s` -> SQLite `?`
        query = query.replace('%s', '?')
        # 2. Migrate Schema tokens: MySQL `AUTO_INCREMENT` -> SQLite `AUTOINCREMENT`
        query = query.replace('AUTO_INCREMENT', 'AUTOINCREMENT')
        
        if args:
            self.cursor.execute(query, args)
        else:
            self.cursor.execute(query)
            
    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if row else None
        
    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
        
    def close(self):
        self.cursor.close()

class SQLiteDBWrapper:
    """Wrapper that acts like a PyMySQL Connection for our SQLite database."""
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def cursor(self):
        return SQLiteCursorWrapper(self.conn)
        
    def commit(self):
        self.conn.commit()
        
    def rollback(self):
        self.conn.rollback()
        
    def close(self):
        self.conn.close()

def get_db():
    if 'db' not in g:
        host = os.environ.get('MYSQL_HOST', 'localhost')
        
        # If the environment is NOT localhost, attempt to use the Vercel PyMySQL driver
        if host != 'localhost' or os.environ.get('FORCE_MYSQL', '0') == '1':
            try:
                g.db = pymysql.connect(
                    host=host,
                    user=os.environ.get('MYSQL_USER', 'root'),
                    password=os.environ.get('MYSQL_PASSWORD', ''),
                    database=os.environ.get('MYSQL_DB', 'apexcare_erp'),
                    cursorclass=pymysql.cursors.DictCursor
                )
            except pymysql.MySQLError as e:
                print(f"[DB] PyMySQL Cloud Connect Error, safely falling back to local SQLite: {e}")
                if os.environ.get('VERCEL') == '1':
                    db_path = '/tmp/apexcare.db'
                else:
                    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apexcare.db')
                g.db = SQLiteDBWrapper(db_path)
        else:
            # Safely use SQLite natively if operating locally
            if os.environ.get('VERCEL') == '1':
                db_path = '/tmp/apexcare.db'
            else:
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apexcare.db')
            g.db = SQLiteDBWrapper(db_path)
    return g.db

def close_db(exc=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        # First ensure database exists if connecting globally (or locally)
        try:
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    username   VARCHAR(255) NOT NULL UNIQUE,
                    password   VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Insert admin if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (username, password)
                    VALUES ('admin', 'admin123');
                """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name       VARCHAR(255) NOT NULL,
                    age        INTEGER NOT NULL,
                    disease    VARCHAR(255) NOT NULL,
                    contact    VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                    id             INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name           VARCHAR(255) NOT NULL,
                    qualification  VARCHAR(255) NOT NULL,
                    specialization VARCHAR(255) NOT NULL,
                    experience     INTEGER NOT NULL,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id  INTEGER NOT NULL,
                    date       VARCHAR(255) NOT NULL,
                    status     VARCHAR(255) NOT NULL DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS beds (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    bed_number VARCHAR(255) NOT NULL,
                    status     VARCHAR(255) NOT NULL DEFAULT 'Available',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name       VARCHAR(255) NOT NULL,
                    course     VARCHAR(255) NOT NULL,
                    year       INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faculty (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name       VARCHAR(255) NOT NULL,
                    department VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id          INTEGER PRIMARY KEY AUTO_INCREMENT,
                    course_name VARCHAR(255) NOT NULL,
                    credits     INTEGER NOT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    student_id INTEGER NOT NULL,
                    date       VARCHAR(255) NOT NULL,
                    status     VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fees (
                    id         INTEGER PRIMARY KEY AUTO_INCREMENT,
                    student_id INTEGER NOT NULL,
                    amount     REAL NOT NULL,
                    status     VARCHAR(255) NOT NULL DEFAULT 'Unpaid',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                );
            """)

            db.commit()
            cursor.close()
        except Exception as e:
            print(f"[DB INIT INIT] Error: {e}")
