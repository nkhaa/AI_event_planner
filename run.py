#!/usr/bin/env python3
"""
AI Event Planner - Startup Script
Энэ файлыг ажиллуулснаар сервер эхлэнэ.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from src.server import app, init_db

if __name__ == "__main__":
    print("=" * 60)
    print("🎉 AI Event Planner серверийг эхлүүлж байна...")
    print("=" * 60)
    print()
    print("📍 Сервер: http://localhost:4890")
    print("📍 Хаяг: http://127.0.0.1:4890")
    print()
    print("⚠️  Серверийг зогсоох: Ctrl+C дарна уу")
    print()
    print("=" * 60)
    
    # Initialize database
    init_db()
    print("✅ Өгөгдлийн сан амжилттай эхлүүллээ")
    
    # Run the app
    app.run(debug=True, port=4890, host='0.0.0.0')