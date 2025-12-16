import sqlite3
from src.db import DB_PATH

def get_login_history(identifier: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT identifier, success, timestamp FROM login_history WHERE identifier = ?",
        (identifier,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
