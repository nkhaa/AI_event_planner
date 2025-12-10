from flask import Flask, request, jsonify
from src.auth import register, login
from src.history import get_login_history

app = Flask(__name__)

@app.post("/register")
def api_register():
    data = request.json
    res = register(data["email"], data["password"])
    return jsonify({"message": "Бүртгэл амжилттай."})

@app.post("/login")
def api_login():
    data = request.json
    try:
        res = login(data["email"], data["password"])
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.get("/history/<email>")
def api_history(email):
    history = get_login_history(email)
    return jsonify([
        {"timestamp": h[2], "success": "Амжилттай" if h[1] == 1 else "Амжилтгүй"}
        for h in history
    ])

if __name__ == "__main__":
    app.run(port=5000, debug=True)

