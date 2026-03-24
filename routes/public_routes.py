from flask import Blueprint, jsonify
from db import get_db

public_bp = Blueprint('public', __name__)

@public_bp.route('/scholarships', methods=['GET'])
def get_public_scholarships():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM scholarships LIMIT 6")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

@public_bp.route('/events', methods=['GET'])
def get_public_events():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM events LIMIT 6")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

@public_bp.route('/ngos', methods=['GET'])
def get_public_ngos():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM ngos")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

@public_bp.route('/mentor-posts', methods=['GET'])
def get_public_mentor_posts():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM mentor_posts LIMIT 4")
    rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])
