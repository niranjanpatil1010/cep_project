from flask import Blueprint, request, jsonify
from middleware import auth_middleware, role_middleware, notify
from db import get_db

mentor_bp = Blueprint('mentor', __name__)

@mentor_bp.route('/posts', methods=['GET'])
@auth_middleware()
@role_middleware(['mentor'])
def get_my_posts():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM mentor_posts WHERE mentor_id = ?", (request.user['id'],))
    posts = []
    for row in cur.fetchall():
        d = dict(row)
        d['tags'] = d['tags'].split(',') if d['tags'] else []
        posts.append(d)
    return jsonify(posts)

@mentor_bp.route('/posts', methods=['POST'])
@auth_middleware()
@role_middleware(['mentor'])
def create_post():
    data = request.json
    db = get_db()
    cur = db.cursor()
    
    tags = data.get('tags', [])
    if isinstance(tags, list):
        tags = ','.join(tags)
        
    cur.execute("""
        INSERT INTO mentor_posts (mentor_id, title, content, tags, resource_url)
        VALUES (?, ?, ?, ?, ?)
    """, (request.user['id'], data.get('title'), data.get('content'), tags, data.get('resourceUrl')))
    db.commit()
    
    cur.execute("SELECT id FROM users WHERE role='student'")
    for u in cur.fetchall():
        notify(u['id'], f"New guidance post from {request.user['name']}: {data.get('title')}", "info")
        
    return jsonify({"message": "Post created"}), 201

@mentor_bp.route('/posts/<int:post_id>', methods=['PUT'])
@auth_middleware()
@role_middleware(['mentor'])
def update_post(post_id):
    data = request.json
    db = get_db()
    cur = db.cursor()
    
    tags = data.get('tags')
    if isinstance(tags, list):
        tags = ','.join(tags)
        
    cur.execute("""
        UPDATE mentor_posts SET title = ?, content = ?, tags = ?, resource_url = ?
        WHERE id = ? AND mentor_id = ?
    """, (data.get('title'), data.get('content'), tags, data.get('resourceUrl'), post_id, request.user['id']))
    db.commit()
    return jsonify({"message": "Post updated"})

@mentor_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['mentor'])
def delete_post(post_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM mentor_posts WHERE id = ? AND mentor_id = ?", (post_id, request.user['id']))
    db.commit()
    return jsonify({"message": "Post deleted"})
