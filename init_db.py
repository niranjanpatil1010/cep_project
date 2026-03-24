import sqlite3
import os
import json

DATABASE = 'database.db'

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

    # Insert user (password should be hashed in production, but keeping it simple for now)
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('Student One', 'student1@test.com', 'password', 'student'))
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('NGO Admin', 'ngo1@test.com', 'password', 'ngo'))
    cur.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                ('Mentor Alpha', 'mentor1@test.com', 'password', 'mentor'))

    # Insert NGO
    # We know NGO Admin is user id 2
    cur.execute("INSERT INTO ngos (user_id, name, description, location) VALUES (?, ?, ?, ?)",
                (2, 'EduCare Foundation', 'Providing education for all.', 'Mumbai'))

    # Insert events
    cur.execute("INSERT INTO events (title, description, date, location, ngo_id) VALUES (?, ?, ?, ?, ?)",
                ('Career Guidance Seminar', 'Learn about opportunities after graduation.', '2026-04-10', 'Mumbai', 1))

    # Insert scholarships
    cur.execute("INSERT INTO scholarships (title, description, eligibility, deadline, ngo_id, amount) VALUES (?, ?, ?, ?, ?, ?)",
                ('Tech Scholars Program', 'Scholarship for CS students.', '2nd Year CS Students', '2026-05-01', 1, '25000'))

    # Insert mentor post
    cur.execute("INSERT INTO mentor_posts (mentor_id, title, content, tags) VALUES (?, ?, ?, ?)",
                (3, 'Beginner Roadmap for DSA', 'Start with arrays and strings, then move to linked lists, trees, and graphs. Practice daily on LeetCode.', 'DSA,Beginner'))

    # Insert notifications
    cur.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                (1, 'Welcome to EduConnect! 🎉', 'info'))
    cur.execute("INSERT INTO notifications (user_id, message, type) VALUES (?, ?, ?)",
                (2, 'Welcome, EduCare Foundation! 🏢', 'info'))

    # Insert a library book
    cur.execute("INSERT INTO library_books (title, subject, condition, ngo_id, status) VALUES (?, ?, ?, ?, ?)",
                ('Introduction to Algorithms', 'Computer Science', 'Good', 1, 'available'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
