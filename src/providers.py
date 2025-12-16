# src/providers.py
from flask import request, jsonify, session
from src.db import get_db

def register_provider():
    if 'user_id' not in session:
        return jsonify({"error": "Нэвтэрч орно уу"}), 401
    
    data = request.json
    
    # Validation
    required_fields = ['name', 'location', 'capacity', 'price', 'packages']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} талбарыг бөглөнө үү"}), 400
    
    try:
        capacity = int(data['capacity'])
        price = int(data['price'])
        
        if capacity <= 0:
            return jsonify({"error": "Хүчин чадал 0-ээс их байх ёстой"}), 400
        if price < 0:
            return jsonify({"error": "Үнэ 0-ээс их байх ёстой"}), 400
            
    except ValueError:
        return jsonify({"error": "Хүчин чадал болон үнэ тоо байх ёстой"}), 400
    
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO providers
            (user_id, name, location, capacity, price, packages, image_url, 
             description, contact_phone, contact_email)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            session['user_id'],
            data["name"],
            data["location"],
            capacity,
            price,
            data["packages"],
            data.get("image_url", ""),
            data.get("description", ""),
            data.get("contact_phone", ""),
            data.get("contact_email", "")
        ))

        conn.commit()
        provider_id = cur.lastrowid
        
        return jsonify({
            "status": "ok",
            "provider_id": provider_id,
            "message": "Үйлчилгээ амжилттай бүртгэгдлээ!"
        })
    except Exception as e:
        return jsonify({"error": f"Алдаа гарлаа: {str(e)}"}), 500

def get_provider_by_id(provider_id):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM providers WHERE id = ?", (provider_id,))
    provider = cur.fetchone()
    
    if provider:
        return jsonify(dict(provider))
    return jsonify({"error": "Үйлчилгээ олдсонгүй"}), 404

def get_my_providers():
    if 'user_id' not in session:
        return jsonify({"error": "Нэвтэрч орно уу"}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM providers 
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session['user_id'],))
    
    providers = [dict(row) for row in cur.fetchall()]
    return jsonify(providers)

def update_provider(provider_id):
    if 'user_id' not in session:
        return jsonify({"error": "Нэвтэрч орно уу"}), 401
    
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    
    # Check ownership
    cur.execute("SELECT user_id FROM providers WHERE id = ?", (provider_id,))
    provider = cur.fetchone()
    
    if not provider or provider['user_id'] != session['user_id']:
        return jsonify({"error": "Энэ үйлчилгээг засах эрхгүй байна"}), 403
    
    # Update fields
    update_fields = []
    values = []
    
    for field in ['name', 'location', 'capacity', 'price', 'packages', 'image_url', 
                  'description', 'contact_phone', 'contact_email']:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        return jsonify({"error": "Шинэчлэх өгөгдөл байхгүй байна"}), 400
    
    values.append(provider_id)
    query = f"UPDATE providers SET {', '.join(update_fields)} WHERE id = ?"
    
    cur.execute(query, values)
    conn.commit()
    
    return jsonify({"status": "ok", "message": "Амжилттай шинэчлэгдлээ"})

def delete_provider(provider_id):
    if 'user_id' not in session:
        return jsonify({"error": "Нэвтэрч орно уу"}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check ownership
    cur.execute("SELECT user_id FROM providers WHERE id = ?", (provider_id,))
    provider = cur.fetchone()
    
    if not provider or provider['user_id'] != session['user_id']:
        return jsonify({"error": "Энэ үйлчилгээг устгах эрхгүй байна"}), 403
    
    cur.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
    conn.commit()
    
    return jsonify({"status": "ok", "message": "Амжилттай устгагдлаа"})