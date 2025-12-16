import hashlib
import sqlite3
from src.db import DB_PATH
from src.errors import ValidationError, NotFoundError

PHONE_MIN_LENGTH = 6
PHONE_MAX_LENGTH = 15


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _detect_identifier(identifier: str):
    """Return tuple(kind, normalized_identifier)."""
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValidationError("Имэйл эсвэл утас оруулна уу.")

    identifier = identifier.strip()
    if "@" in identifier:
        return "email", identifier.lower()

    # Basic phone validation: digits with optional + prefix
    normalized = identifier.replace(" ", "").replace("-", "")
    if normalized.startswith("+"):
        normalized_digits = normalized[1:]
    else:
        normalized_digits = normalized

    if not normalized_digits.isdigit():
        raise ValidationError("Утасны дугаарыг зөв оруулна уу.")
    if not (PHONE_MIN_LENGTH <= len(normalized_digits) <= PHONE_MAX_LENGTH):
        raise ValidationError("Утасны дугаарын урт буруу байна.")

    # store with + if provided
    return "phone", normalized if normalized.startswith("+") else normalized_digits


def register(identifier: str, password: str):
    kind, value = _detect_identifier(identifier)

    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (identifier, kind, password) VALUES (?, ?, ?)",
            (value, kind, hashed),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValidationError("Энэ бүртгэл аль хэдийн үүссэн байна.")
    finally:
        conn.close()

    return {"identifier": value, "kind": kind, "status": "registered"}


def login(identifier: str, password: str):
    kind, value = _detect_identifier(identifier)
    hashed = hash_password(password)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE identifier = ? AND kind = ?",
        (value, kind),
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise NotFoundError("Хэрэглэгч олдсонгүй")

    correct_hash = row[0]
    success = 1 if correct_hash == hashed else 0

    cursor.execute(
        "INSERT INTO login_history (identifier, success) VALUES (?, ?)",
        (value, success)
    )
    conn.commit()
    conn.close()

    if success == 0:
        raise ValidationError("Нууц үг буруу.")

    return {"identifier": value, "kind": kind, "status": "logged_in"}
