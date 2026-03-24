-- schema.sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL, -- 'student', 'ngo', 'mentor', 'admin'
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    is_verified BOOLEAN DEFAULT 0,
    verification_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ngos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    registration_number TEXT,
    address TEXT,
    website TEXT,
    description TEXT,
    location TEXT,
    certificate_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS mentors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    linkedin_profile TEXT,
    resume_path TEXT,
    organization_college TEXT,
    experience_years INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    location TEXT,
    ngo_id INTEGER NOT NULL,
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);

CREATE TABLE IF NOT EXISTS scholarships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    eligibility TEXT,
    deadline TEXT NOT NULL,
    ngo_id INTEGER NOT NULL,
    amount TEXT,
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);

CREATE TABLE IF NOT EXISTS mentor_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT,
    resource_url TEXT,
    FOREIGN KEY (mentor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT 0,
    type TEXT DEFAULT 'info',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scholarship_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    applicant_name TEXT,
    applicant_email TEXT,
    applicant_phone TEXT,
    applicant_education TEXT,
    applicant_gpa TEXT,
    applicant_sop TEXT,
    FOREIGN KEY (scholarship_id) REFERENCES scholarships(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS event_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    student_name TEXT,
    student_email TEXT,
    registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    ngo_id INTEGER NOT NULL,
    ngo_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);

CREATE TABLE IF NOT EXISTS book_donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_title TEXT NOT NULL,
    subject TEXT,
    condition TEXT,
    location TEXT,
    donor_id INTEGER NOT NULL,
    donor_name TEXT,
    ngo_id INTEGER NOT NULL,
    ngo_name TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id),
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);

CREATE TABLE IF NOT EXISTS library_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    condition TEXT,
    ngo_id INTEGER NOT NULL,
    donor_id INTEGER,
    donor_name TEXT,
    donation_id INTEGER,
    status TEXT DEFAULT 'available', -- 'available', 'borrowed', 'requested'
    added_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ngo_id) REFERENCES ngos(id),
    FOREIGN KEY (donor_id) REFERENCES users(id),
    FOREIGN KEY (donation_id) REFERENCES book_donations(id)
);

CREATE TABLE IF NOT EXISTS borrow_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    book_title TEXT,
    student_id INTEGER NOT NULL,
    student_name TEXT,
    student_email TEXT,
    ngo_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected', 'returned'
    requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
    borrowed_at TEXT,
    returned_at TEXT,
    FOREIGN KEY (book_id) REFERENCES library_books(id),
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (ngo_id) REFERENCES ngos(id)
);

CREATE TABLE IF NOT EXISTS student_activity_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id)
);
