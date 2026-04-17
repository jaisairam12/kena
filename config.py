import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'apexcare_erp_secret_xK9mN2pQ7vR')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')        # Change to your MySQL password
    MYSQL_DB = os.environ.get('MYSQL_DB', 'apexcare_erp')
    MYSQL_CURSORCLASS = 'DictCursor'
