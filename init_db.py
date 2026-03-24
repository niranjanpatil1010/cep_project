import sqlite3
import os
import json
import bcrypt

DATABASE = 'database.db'

def hash_pass(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)

    conn = get_db_connection()
    with open('schema.sql') as f:
        conn.executescript(f.read())

    cur = conn.cursor()

    # Insert users
    # Password Rules: 8 chars, 1 upper, 1 lower, 1 number, 1 special
    # Admin password: Admin@123
    cur.execute("INSERT INTO users (name, email, password, role, status, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                ('Admin', 'admin@test.com', hash_pass('Admin@123'), 'admin', 'approved', 1))
    cur.execute("INSERT INTO users (name, email, password, role, status, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                ('Student One', 'student1@test.com', hash_pass('Student@123'), 'student', 'approved', 1))
    cur.execute("INSERT INTO users (name, email, password, role, status, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                ('NGO Admin', 'ngo1@test.com', hash_pass('Ngo@12345'), 'ngo', 'pending', 1))
    cur.execute("INSERT INTO users (name, email, password, role, status, is_verified) VALUES (?, ?, ?, ?, ?, ?)",
                ('Mentor Alpha', 'mentor1@test.com', hash_pass('Mentor@123'), 'mentor', 'pending', 1))

    # Insert NGO
    # We know Admin is ID 1, Student is ID 2, NGO is ID 3, Mentor is ID 4
    cur.execute("INSERT INTO ngos (user_id, name, registration_number, address, website, description, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (3, 'EduCare Foundation', 'NGO12345', '123 MG Road', 'www.educare.org', 'Providing education for all.', 'Mumbai'))
    
    # Insert Mentor
    cur.execute("INSERT INTO mentors (user_id, full_name, linkedin_profile, organization_college, experience_years) VALUES (?, ?, ?, ?, ?)",
                (4, 'Mentor Alpha', 'https://linkedin.com/in/mentor1', 'Tech Institute', 10))

    # Insert events
    cur.execute("INSERT INTO events (title, description, date, location, ngo_id) VALUES (?, ?, ?, ?, ?)",
                ('Career Guidance Seminar', 'Learn about opportunities after graduation.', '2026-04-10', 'Mumbai', 1))

    # Insert scholarships
    cur.execute("INSERT INTO scholarships (title, description, eligibility, deadline, ngo_id, amount) VALUES (?, ?, ?, ?, ?, ?)",
                ('Tech Scholars Program', 'Scholarship for CS students.', '2nd Year CS Students', '2026-05-01', 1, '25000'))

    # Insert mentor post
    cur.execute("INSERT INTO mentor_posts (mentor_id, title, content, tags) VALUES (?, ?, ?, ?)",
                (4, 'Beginner Roadmap for DSA', 'Start with arrays and strings, then move to linked lists, trees, and graphs. Practice daily on LeetCode.', 'DSA,Beginner'))

    # Insert notifications
    cur.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                (2, 'Welcome to EduConnect! 🎉', 'info'))
    cur.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                (3, 'Welcome, EduCare Foundation! 🏢', 'info'))

    # Insert a library book
    cur.execute("INSERT INTO library_books (title, subject, condition, ngo_id, status) VALUES (?, ?, ?, ?, ?)",
                ('Introduction to Algorithms', 'Computer Science', 'Good', 1, 'available'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
