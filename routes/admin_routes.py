from flask import Blueprint, request, jsonify
from db import get_db
from middleware import auth_middleware, role_middleware

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@auth_middleware()
@role_middleware(['admin'])
def list_users():
    role = request.args.get('role')
    status = request.args.get('status')
    
    db = get_db()
    cur = db.cursor()
    
    query = "SELECT id, name, email, role, status, is_verified, created_at FROM users WHERE role != 'admin'"
    params = []
    
    if role:
        query += " AND role = ?"
        params.append(role)
    if status:
        query += " AND status = ?"
        params.append(status)
        
    cur.execute(query, params)
    users = [dict(row) for row in cur.fetchall()]
    
    return jsonify(users), 200

@admin_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@auth_middleware()
@role_middleware(['admin'])
def update_user_status(user_id):
    data = request.json
    new_status = data.get('status')
    
    if new_status not in ['approved', 'rejected', 'pending']:
        return jsonify({"error": "Invalid status"}), 400
        
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
    db.commit()
    
    return jsonify({"message": f"User status updated to {new_status}"}), 200

@admin_bp.route('/users/<int:user_id>/details', methods=['GET'])
@auth_middleware()
@role_middleware(['admin'])
def get_user_details(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    user_data = dict(user)
    user_data.pop('password', None)
    
    if user_data['role'] == 'ngo':
        cur.execute("SELECT * FROM ngos WHERE user_id = ?", (user_id,))
        ngo = cur.fetchone()
        if ngo:
            user_data['ngo_details'] = dict(ngo)
    elif user_data['role'] == 'mentor':
        cur.execute("SELECT * FROM mentors WHERE user_id = ?", (user_id,))
        mentor = cur.fetchone()
        if mentor:
            user_data['mentor_details'] = dict(mentor)
            
    return jsonify(user_data), 200
