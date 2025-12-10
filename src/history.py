import sqlite3
from src.db import DB_PATH

def get_login_history(email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email, success, timestamp FROM login_history WHERE email = ?",
        (email,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
