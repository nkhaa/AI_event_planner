# src/server.py
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from src.db import get_db, init_db
from src.auth import register_user, login_user, logout_user, get_current_user
from src.providers import (
    register_provider,
    get_provider_by_id,
    get_my_providers,
    update_provider,
    delete_provider
)
import os
from src.auth import require_auth

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ✅ SECRET KEY (Railway-compatible)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# ✅ CORS
CORS(app, supports_credentials=True)

# ---------------- PAGE ROUTES ----------------
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
@app.route("/api/stats/providers", methods=["GET"])
@require_auth
def provider_stats():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM providers")
    count = cur.fetchone()[0]
    return jsonify({"total_providers": count}), 200
@app.route("/api/stats", methods=["GET"])
@require_auth
def stats():
    db = get_db()
    cur = db.cursor()

    # users count
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    # providers count
    cur.execute("SELECT COUNT(*) FROM providers")
    total_providers = cur.fetchone()[0]

    return jsonify({
        "users": total_users,
        "providers": total_providers
    }), 200

@app.route("/search")
def search_page():
    return render_template("search.html")

# ---------------- AUTH ROUTES ----------------
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

@app.route("/api/providers/register", methods=["POST"])
def provider_register():
    return register_provider()

@app.route("/api/stats/users", methods=["GET"])
@require_auth
def user_stats():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    return jsonify({"total_users": count}), 200

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

# ---------------- SEARCH ROUTES ----------------
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

    cur.execute(query, params)
    results = [dict(row) for row in cur.fetchall()]
    return jsonify(results)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    init_db()

    # ✅ Railway-compatible PORT
    port = int(os.environ.get("PORT", 4890))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
