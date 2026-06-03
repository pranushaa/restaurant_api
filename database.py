import mysql.connector
import os

def call_database():
    ca_path = os.path.join(os.path.dirname(__file__), 'ca.pem')
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 13080)),
        ssl_ca=ca_path if os.path.exists(ca_path) else None,
        ssl_verify_cert=True if os.path.exists(ca_path) else False
    )