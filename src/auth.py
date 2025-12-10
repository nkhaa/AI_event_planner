import hashlib
import sqlite3
from src.db import DB_PATH, init_db
from src.errors import ValidationError, NotFoundError

init_db()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register(email: str, password: str):
    if "@" not in email:
        raise ValidationError("Имэйл буруу байна.")

    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
    except Exception:
        raise ValidationError("Энэ имэйл өмнө бүртгэлтэй байна.")
    finally:
        conn.close()

    return {"email": email, "status": "registered"}


def login(email: str, password: str):
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise NotFoundError("Хэрэглэгч олдсонгүй")

    correct_hash = row[0]
    success = 1 if correct_hash == hashed else 0

    cursor.execute(
        "INSERT INTO login_history (email, success) VALUES (?, ?)",
        (email, success)
    )
    conn.commit()
    conn.close()

    if success == 0:
        raise ValidationError("Нууц үг буруу.")

    return {"email": email, "status": "logged_in"}
