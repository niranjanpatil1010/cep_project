from flask import request, jsonify, current_app
import jwt
from functools import wraps
import db
import os

def auth_middleware():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'message': 'Authorization required'}), 401
            
            token = auth_header.split(' ')[1]
            try:
                secret_key = current_app.config.get('SECRET_KEY', 'super-secret-key')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
                user_id = payload['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Invalid token'}), 401
                
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
            
            if not user:
                return jsonify({'message': 'User not found'}), 401
            
            user_data = dict(user)
            # Check if user is approved and verified
            if user_data['status'] == 'pending' and user_data['role'] != 'admin':
                return jsonify({'message': 'Your account is under verification'}), 403
            if user_data['status'] == 'rejected':
                return jsonify({'message': 'Your account was rejected. Contact admin'}), 403
            if not user_data['is_verified']:
                return jsonify({'message': 'Please verify your email first'}), 403

            request.user = user_data
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
