from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from src.auth import register, login
from src.history import get_login_history
from src.errors import ValidationError, NotFoundError
from src.db import init_db
from src.providers import create_provider, save_provider, register_provider

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
    static_url_path="/static",
)

CORS(app)

# Initialize DB (DEV / TEST)
init_db()


# ========== CORS ==========
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return jsonify({}), 200


# ========== ERROR HANDLERS ==========
@app.errorhandler(ValidationError)
@app.errorhandler(NotFoundError)
def handle_custom_error(e):
    return jsonify({"status": "error", "message": str(e)}), 400


@app.errorhandler(404)
def handle_404(e):
    return jsonify({"status": "error", "message": "Энд олдсонгүй"}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"status": "error", "message": str(e)}), 500


# ========== UI ==========
@app.get("/")
def home():
    return render_template("index.html")


# ========== PROVIDER REGISTER ==========
@app.post("/api/providers/register")
def api_provider_register():
    try:
        data = request.get_json(silent=True) or {}
        provider = register_provider(
            name=data.get("name"),
            capacity=data.get("capacity"),
            price=data.get("price"),
            packages=data.get("packages"),
            image_url=data.get("image_url"),
            available_dates=data.get("available_dates"),
            location=data.get("location"),
        )

        save_provider(provider)
        return jsonify({"message": "Үйлчилгээ амжилттай бүртгэгдлээ"}), 201
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ========== USER REGISTER ==========
@app.post("/register")
def api_register():
    try:
        data = request.get_json(silent=True) or {}
        identifier = data.get("identifier") or data.get("email")

        if not identifier or "password" not in data:
            raise ValidationError("Имэйл эсвэл утас, нууц үг шаардлагатай")

        result = register(identifier, data["password"])
        return jsonify({"status": "ok", **result})
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ========== LOGIN ==========
@app.post("/login")
def api_login():
    try:
        data = request.get_json(silent=True) or {}
        identifier = data.get("identifier") or data.get("email")

        if not identifier or "password" not in data:
            raise ValidationError("Имэйл эсвэл утас, нууц үг шаардлагатай")

        return jsonify(login(identifier, data["password"]))
    except ValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except NotFoundError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ========== LOGIN HISTORY ==========
@app.get("/history/<identifier>")
def api_history(identifier):
    history = get_login_history(identifier)

    return jsonify([
        {
            "timestamp": h[2],
            "success": "Амжилттай" if h[1] == 1 else "Амжилтгүй"
        }
        for h in history
    ])


if __name__ == "__main__":
    app.run(port=5000, debug=True)
