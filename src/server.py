# src/server.py
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from src.db import get_db, init_db
from src.auth import register_user, login_user, logout_user, get_current_user
from src.providers import (register_provider, get_provider_by_id, get_my_providers,
                           update_provider, delete_provider)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# Secret key for sessions
app.secret_key = 'your-secret-key-change-this-in-production'
CORS(app, supports_credentials=True)

# ---- PAGE ROUTES ----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return render_template("index.html")
    return render_template("dashboard.html")

@app.route("/provider-register")
def provider_register_page():
    user = get_current_user()
    if not user:
        return render_template("index.html")
    return render_template("provider.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

# ---- AUTH ROUTES ----
@app.route("/register", methods=["POST"])
def register():
    return register_user()

@app.route("/login", methods=["POST"])
def login():
    return login_user()

@app.route("/logout", methods=["POST"])
def logout():
    return logout_user()

@app.route("/api/current-user")
def current_user():
    user = get_current_user()
    if user:
        return jsonify(user)
    return jsonify({"error": "Not authenticated"}), 401

# ---- PROVIDER ROUTES ----
@app.route("/api/providers/register", methods=["POST"])
def provider_register():
    return register_provider()

@app.route("/api/providers/<int:provider_id>")
def provider_detail(provider_id):
    return get_provider_by_id(provider_id)

@app.route("/api/providers/my")
def my_providers():
    return get_my_providers()

@app.route("/api/providers/<int:provider_id>", methods=["PUT"])
def provider_update(provider_id):
    return update_provider(provider_id)

@app.route("/api/providers/<int:provider_id>", methods=["DELETE"])
def provider_delete(provider_id):
    return delete_provider(provider_id)

# ---- SEARCH ROUTES ----
@app.route("/api/providers/search")
def search_providers():
    location = request.args.get("location", "")
    min_price = request.args.get("min_price", 0)
    max_price = request.args.get("max_price", 999999999)
    capacity = request.args.get("capacity", 0)
    event_type = request.args.get("event_type", "")

    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT * FROM providers
        WHERE location LIKE ?
        AND price BETWEEN ? AND ?
        AND capacity >= ?
    """
    
    params = [f"%{location}%", min_price, max_price, capacity]
    
    if event_type:
        query += " AND packages LIKE ?"
        params.append(f"%{event_type}%")
    
    query += " ORDER BY rating DESC, total_bookings DESC"
    
    cur.execute(query, params)
    results = [dict(row) for row in cur.fetchall()]
    
    return jsonify(results)

# ---- STATS ROUTES ----
@app.route("/api/stats")
def stats():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Нэвтэрч орно уу"}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    if user['user_type'] == 'provider':
        # Provider stats
        cur.execute("""
            SELECT COUNT(*) as total_providers 
            FROM providers 
            WHERE user_id = ?
        """, (user['user_id'],))
        providers_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) as total_bookings
            FROM bookings b
            JOIN providers p ON b.provider_id = p.id
            WHERE p.user_id = ?
        """, (user['user_id'],))
        bookings_count = cur.fetchone()[0]
        
        return jsonify({
            "total_providers": providers_count,
            "total_bookings": bookings_count,
            "user_type": "provider"
        })
    else:
        # User stats
        cur.execute("""
            SELECT COUNT(*) as total_bookings
            FROM bookings
            WHERE user_id = ?
        """, (user['user_id'],))
        bookings_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) as total_providers FROM providers")
        providers_count = cur.fetchone()[0]
        
        return jsonify({
            "total_bookings": bookings_count,
            "total_providers": providers_count,
            "user_type": "user"
        })

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=4890)