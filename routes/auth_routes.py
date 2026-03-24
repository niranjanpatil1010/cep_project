from flask import Blueprint, request, jsonify
from db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    db = get_db()
    
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (data.get('name'), data.get('email'), data.get('password'), data.get('role')))
        user_id = cur.lastrowid
        
        if data.get('role') == 'ngo':
            cur.execute("INSERT INTO ngos (user_id, name) VALUES (?, ?)", (user_id, data.get('orgName', data.get('name'))))
            
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    db = get_db()
    
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", 
                (data.get('email'), data.get('password')))
    user = cur.fetchone()
    
    if user:
        user_dict = dict(user)
        user_dict.pop('password', None)
        
        if user_dict['role'] == 'ngo':
            cur.execute("SELECT * FROM ngos WHERE user_id = ?", (user_dict['id'],))
            ngo = cur.fetchone()
            if ngo:
                user_dict['ngoId'] = ngo['id']
                user_dict['orgName'] = ngo['name']
                
        token = f"fake-jwt-token-{user_dict['id']}"
        return jsonify({"token": token, "user": user_dict}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    # Simulate auth
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Auth required'}), 401
    token = auth_header.split(' ')[1]
    try:
        user_id = int(token.split('-')[-1])
    except:
        return jsonify({'message': 'Invalid token'}), 401
        
    data = request.json
    db = get_db()
    cur = db.cursor()
    
    cur.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (data.get('name'), data.get('email'), user_id))
    db.commit()
    
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cur.fetchone())
    user.pop('password', None)
    
    if user['role'] == 'ngo':
        cur.execute("SELECT * FROM ngos WHERE user_id = ?", (user['id'],))
        ngo = cur.fetchone()
        if ngo:
            user['ngoId'] = ngo['id']
            user['orgName'] = ngo['name']
    
    return jsonify({"message": "Profile updated", "user": user}), 200
