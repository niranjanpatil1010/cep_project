from flask import Flask, jsonify, render_template
from flask_cors import CORS
import db

# Import Blueprints
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.ngo_routes import ngo_bp
from routes.mentor_routes import mentor_bp
from routes.public_routes import public_bp
from routes.admin_routes import admin_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

import os
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Teardown DB connection after each request
app.teardown_appcontext(db.close_connection)

# Register Blueprints for API
app.register_blueprint(public_bp, url_prefix='/api/public')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(ngo_bp, url_prefix='/api/ngo')
app.register_blueprint(mentor_bp, url_prefix='/api/mentor')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# --- Frontend Routes (HTML view) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/ngo-dashboard')
def ngo_dashboard():
    return render_template('ngo_dashboard.html')

@app.route('/mentor-dashboard')
def mentor_dashboard():
    return render_template('mentor_dashboard.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Community Platform Flask API is running"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
