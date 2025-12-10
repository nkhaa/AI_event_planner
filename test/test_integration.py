from src.auth import register, login
from src.history import get_login_history
from src.db import init_db

def test_full_login_flow():
    init_db()

    # 1. Register
    reg = register("miho@example.com", "12345")
    assert reg["status"] == "registered"

    # 2. Login success
    result = login("miho@example.com", "12345")
    assert result["status"] == "logged_in"

    history = get_login_history("miho@example.com")
    assert len(history) >= 1
    assert history[-1][1] == 1  # success field
