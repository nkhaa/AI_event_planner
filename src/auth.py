# src/auth.py
from flask import request, jsonify, session
from src.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import re
from functools import wraps

def is_valid_identifier(identifier):
    """Validate email or phone number"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    phone_pattern = r'^[0-9]{8,11}$'
    
    return re.match(email_pattern, identifier) or re.match(phone_pattern, identifier)

def register_user():
    data = request.json
    
    if not data.get("identifier") or not data.get("password"):
        return jsonify({"error": "Бүх талбарыг бөглөнө үү"}), 400
    
    if not is_valid_identifier(data["identifier"]):
        return jsonify({"error": "И-мэйл эсвэл утасны дугаар буруу байна"}), 400
    
    if len(data["password"]) < 6:
        return jsonify({"error": "Нууц үг хамгийн багадаа 6 тэмдэгт байх ёстой"}), 400
    
    conn = get_db()
    cur = conn.cursor()

    try:
        hashed_password = generate_password_hash(data["password"])
        cur.execute(
            "INSERT INTO users(identifier, password, user_type) VALUES (?,?,?)",
            (data["identifier"], hashed_password, data.get("user_type", "user"))
        )
        conn.commit()
        
        # Auto login after registration
        user_id = cur.lastrowid
        session['user_id'] = user_id
        session['identifier'] = data["identifier"]
        session['user_type'] = data.get("user_type", "user")
        
        return jsonify({
            "status": "ok",
            "user_id": user_id,
            "user_type": session['user_type']
        })
    except Exception as e:
        return jsonify({"error": "Энэ и-мэйл эсвэл утасны дугаар аль хэдийн бүртгэлтэй байна"}), 400

def login_user():
    data = request.json
    
    if not data.get("identifier") or not data.get("password"):
        return jsonify({"error": "Бүх талбарыг бөглөнө үү"}), 400
    
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE identifier=?",
        (data["identifier"],)
    )

    user = cur.fetchone()
    
    if user and check_password_hash(user["password"], data["password"]):
        session['user_id'] = user["id"]
        session['identifier'] = user["identifier"]
        session['user_type'] = user["user_type"]
        
        return jsonify({
            "status": "ok",
            "user_type": user["user_type"]
        })
    
    return jsonify({"error": "И-мэйл эсвэл нууц үг буруу байна"}), 401

def logout_user():
    session.clear()
    return jsonify({"status": "ok"})

def get_current_user():
    if 'user_id' in session:
        return {
            "user_id": session['user_id'],
            "identifier": session['identifier'],
            "user_type": session['user_type']
        }
    return None
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper