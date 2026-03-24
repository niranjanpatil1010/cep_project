import sqlite3
from flask import request, jsonify
from functools import wraps
import db

def auth_middleware():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'message': 'Authorization required'}), 401
            
            token = auth_header.split(' ')[1]
            try:
                # Our mock token format: fake-jwt-token-{id}
                user_id = int(token.split('-')[-1])
            except:
                return jsonify({'message': 'Invalid token format'}), 401
                
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
            
            if not user:
                return jsonify({'message': 'User not found'}), 401
                
            request.user = dict(user)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_middleware(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user') or request.user['role'] not in allowed_roles:
                return jsonify({'message': 'Access denied: insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def notify(user_id, message, type='info'):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                (user_id, message, type))
    conn.commit()
