from flask import Blueprint, request, jsonify, current_app
from db import get_db
import bcrypt
import jwt
import datetime
import re
import uuid
import os
# from utils.mail_utils import send_verification_email

auth_bp = Blueprint('auth', __name__)

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@auth_bp.route('/register', methods=['POST'])
def register():
    # Check if request is multipart
    if request.content_type.startswith('multipart/form-data'):
        data = request.form
        files = request.files
    else:
        data = request.json
        files = {}

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')
    role = data.get('role')

    if not all([name, email, password, confirm_password, role]):
        return jsonify({"error": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if not validate_password(password):
        return jsonify({"error": "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character"}), 400

    db = get_db()
    cur = db.cursor()
    
    # Check if user exists
    cur.execute("SELECT id FROM users WHERE email = ?" , (email,))
    if cur.fetchone():
        return jsonify({"error": "Email already registered"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Initial status: approved for students, pending for others
    initial_status = 'approved' if role == 'student' else 'pending'

    try:
        cur.execute("INSERT INTO users (name, email, password, role, status, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, hashed_password, role, initial_status, 1))
        user_id = cur.lastrowid
        
        if role == 'ngo':
            cert = files.get('certificate')
            cert_path = None
            if cert:
                filename = f"ngo_{user_id}_{cert.filename}"
                cert_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                cert.save(cert_path)

            cur.execute("INSERT INTO ngos (user_id, name, registration_number, address, website, certificate_path) VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, data.get('orgName', name), data.get('regNo'), data.get('address'), data.get('website'), cert_path))
        elif role == 'mentor':
            resume = files.get('resume')
            resume_path = None
            if resume:
                filename = f"mentor_{user_id}_{resume.filename}"
                resume_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                resume.save(resume_path)

            cur.execute("INSERT INTO mentors (user_id, full_name, linkedin_profile, organization_college, experience_years, resume_path) VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, name, data.get('linkedin'), data.get('organization'), data.get('experience'), resume_path))
            
        db.commit()
        return jsonify({"message": "Registration successful! " + ("You can login now." if role == 'student' else "Your account is awaiting admin approval.")}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400


# Removed verification route

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing credentials"}), 400
        
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    user_data = dict(user)
    
    if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Check status (approval)
    if user_data['status'] == 'pending' and user_data['role'] != 'admin':
        return jsonify({"error": "Your account is under verification. We will notify you once approved."}), 403
    elif user_data['status'] == 'rejected':
        return jsonify({"error": "Your account was rejected. Please contact admin for more information."}), 403
        
    # Generate JWT
    secret_key = current_app.config.get('SECRET_KEY', 'super-secret-key')
    payload = {
        'user_id': user_data['id'],
        'role': user_data['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    user_data.pop('password', None)
    user_data.pop('verification_token', None)
    
    if user_data['role'] == 'ngo':
        cur.execute("SELECT * FROM ngos WHERE user_id = ?", (user_data['id'],))
        ngo = cur.fetchone()
        if ngo:
            user_data['ngoId'] = ngo['id']
            user_data['orgName'] = ngo['name']
    elif user_data['role'] == 'mentor':
        cur.execute("SELECT * FROM mentors WHERE user_id = ?", (user_data['id'],))
        mentor = cur.fetchone()
        if mentor:
            user_data['mentorId'] = mentor['id']
            user_data['fullName'] = mentor['full_name']
            
    return jsonify({"token": token, "user": user_data}), 200

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    # This would typically use @auth_middleware but for now keeping it simple as before but fixed
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'message': 'Auth required'}), 401
    
    token = auth_header.split(' ')[1]
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'super-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        user_id = payload['user_id']
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
    
    return jsonify({"message": "Profile updated", "user": user}), 200
