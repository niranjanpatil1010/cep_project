from flask import Blueprint, request, jsonify
from middleware import auth_middleware, role_middleware, notify
from db import get_db

ngo_bp = Blueprint('ngo', __name__)

@ngo_bp.route('/profile', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_profile():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo = cur.fetchone()
    if not ngo:
        return jsonify({'message': 'NGO profile not found'}), 404
    d = dict(ngo)
    d['email'] = request.user['email']
    return jsonify(d)

@ngo_bp.route('/analytics', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_analytics():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo_row = cur.fetchone()
    if not ngo_row:
        return jsonify({
            "totalStudentsHelped": 0, "libraryBooks": 0, "activeScholarships": 0, 
            "totalEvents": 0, "totalRegistrations": 0, "booksDistributed": 0,
            "totalScholarshipApplications": 0, "availableBooks": 0
        })
    ngo_id = ngo_row['id']
    
    cur.execute("SELECT COUNT(*) as c FROM applications a JOIN scholarships s ON a.scholarship_id = s.id WHERE s.ngo_id = ? AND a.status = 'approved'", (ngo_id,))
    total_students_helped = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM applications a JOIN scholarships s ON a.scholarship_id = s.id WHERE s.ngo_id = ?", (ngo_id,))
    total_scholarship_applications = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM library_books WHERE ngo_id = ?", (ngo_id,))
    library_books = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM library_books WHERE ngo_id = ? AND status='available'", (ngo_id,))
    available_books = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM scholarships WHERE ngo_id = ?", (ngo_id,))
    active_scholarships = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM events WHERE ngo_id = ?", (ngo_id,))
    total_events = cur.fetchone()['c']
    
    cur.execute("SELECT COUNT(*) as c FROM event_registrations r JOIN events e ON r.event_id = e.id WHERE e.ngo_id = ?", (ngo_id,))
    total_registrations = cur.fetchone()['c']
    
    # Books distributed could be borrows approved
    cur.execute("SELECT COUNT(*) as c FROM borrow_requests WHERE ngo_id = ? AND (status='approved' OR status='returned')", (ngo_id,))
    books_dist = cur.fetchone()['c']
    
    return jsonify({
        "totalStudentsHelped": total_students_helped,
        "libraryBooks": library_books,
        "activeScholarships": active_scholarships,
        "totalEvents": total_events,
        "totalRegistrations": total_registrations,
        "booksDistributed": books_dist,
        "totalScholarshipApplications": total_scholarship_applications,
        "availableBooks": available_books
    })

@ngo_bp.route('/my-events', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def my_events():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("SELECT * FROM events WHERE ngo_id = ?", (ngo_id,))
    events = []
    for row in cur.fetchall():
        d = dict(row)
        cur.execute("SELECT COUNT(*) as c FROM event_registrations WHERE event_id = ?", (d['id'],))
        d['registrationCount'] = cur.fetchone()['c']
        events.append(d)
    return jsonify(events)

@ngo_bp.route('/events', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def create_event():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo = cur.fetchone()
    if not ngo: return jsonify({"error": "NGO profile missing"}), 404
    
    cur.execute("""
        INSERT INTO events (title, description, date, location, ngo_id)
        VALUES (?, ?, ?, ?, ?)
    """, (data.get('title'), data.get('description'), data.get('date'), data.get('location'), ngo['id']))
    db.commit()
    
    # Notify students
    cur.execute("SELECT id FROM users WHERE role='student'")
    for u in cur.fetchall():
        notify(u['id'], f"📅 New event by {ngo['name']}: \"{data.get('title')}\"", 'event')
        
    return jsonify({"message": "Event created successfully"}), 201

@ngo_bp.route('/events/<int:event_id>', methods=['PUT'])
@auth_middleware()
@role_middleware(['ngo'])
def update_event(event_id):
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("UPDATE events SET title=?, description=?, date=?, location=? WHERE id=? AND ngo_id=?", 
                (data.get('title'), data.get('description'), data.get('date'), data.get('location'), event_id, ngo_id))
    db.commit()
    return jsonify({"message": "Event updated successfully"})

@ngo_bp.route('/events/<int:event_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['ngo'])
def delete_event(event_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("DELETE FROM events WHERE id=? AND ngo_id=?", (event_id, ngo_id))
    cur.execute("DELETE FROM event_registrations WHERE event_id=?", (event_id,))
    db.commit()
    return jsonify({"message": "Event deleted successfully"})

@ngo_bp.route('/my-scholarships', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def my_scholarships():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("SELECT * FROM scholarships WHERE ngo_id = ?", (ngo_id,))
    return jsonify([dict(row) for row in cur.fetchall()])

@ngo_bp.route('/scholarships', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def create_scholarship():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo = cur.fetchone()
    if not ngo: return jsonify({"error": "NGO profile missing"}), 404
    
    cur.execute("""
        INSERT INTO scholarships (title, description, eligibility, deadline, amount, ngo_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.get('title'), data.get('description'), data.get('eligibility'), data.get('deadline'), data.get('amount'), ngo['id']))
    db.commit()
    
    cur.execute("SELECT id FROM users WHERE role='student'")
    for u in cur.fetchall():
        notify(u['id'], f"🏆 New scholarship from {ngo['name']}: \"{data.get('title')}\"", 'scholarship')
        
    return jsonify({"message": "Scholarship created successfully"}), 201

@ngo_bp.route('/scholarships/<int:sch_id>', methods=['PUT'])
@auth_middleware()
@role_middleware(['ngo'])
def update_scholarship(sch_id):
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("UPDATE scholarships SET title=?, description=?, eligibility=?, deadline=?, amount=? WHERE id=? AND ngo_id=?", 
                (data.get('title'), data.get('description'), data.get('eligibility'), data.get('deadline'), data.get('amount'), sch_id, ngo_id))
    db.commit()
    return jsonify({"message": "Scholarship updated successfully"})

@ngo_bp.route('/scholarships/<int:sch_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['ngo'])
def delete_scholarship(sch_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("DELETE FROM scholarships WHERE id=? AND ngo_id=?", (sch_id, ngo_id))
    cur.execute("DELETE FROM applications WHERE scholarship_id=?", (sch_id,))
    db.commit()
    return jsonify({"message": "Scholarship deleted"})

@ngo_bp.route('/applications', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_applications():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("""
        SELECT a.*, s.title as scholarshipTitle, u.name as studentName, u.email as studentEmail
        FROM applications a
        JOIN scholarships s ON a.scholarship_id = s.id
        JOIN users u ON a.student_id = u.id
        WHERE s.ngo_id = ?
    """, (ngo_id,))
    
    apps = []
    for row in cur.fetchall():
        d = dict(row)
        d['dateApplied'] = d['applied_at']
        d['applicantDetails'] = {
            'fullName': d['applicant_name'],
            'email': d['applicant_email'],
            'phone': d['applicant_phone'],
            'educationLevel': d['applicant_education'],
            'gpa': d['applicant_gpa'],
            'statementOfPurpose': d['applicant_sop']
        }
        apps.append(d)
    return jsonify(apps)

@ngo_bp.route('/applications/<int:app_id>/approve', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def approve_application(app_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo = cur.fetchone()
    if not ngo: return jsonify({"error": "NGO profile missing"}), 404
    
    cur.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    app = cur.fetchone()
    
    cur.execute("SELECT title FROM scholarships WHERE id = ?", (app['scholarship_id'],))
    sch = cur.fetchone()
    
    cur.execute("UPDATE applications SET status='approved' WHERE id=?", (app_id,))
    db.commit()
    notify(app['student_id'], f"🎉 Congratulations! Your application for \"{sch['title']}\" has been APPROVED by {ngo['name']}!", 'scholarship')
    return jsonify({"message": "Application approved!"})

@ngo_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def reject_application(app_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE applications SET status='rejected' WHERE id=?", (app_id,))
    db.commit()
    
    cur.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    app = cur.fetchone()
    cur.execute("SELECT title FROM scholarships WHERE id = ?", (app['scholarship_id'],))
    sch = cur.fetchone()
    notify(app['student_id'], f"Your application for \"{sch['title']}\" was not selected this time. Keep trying!", 'scholarship')
    return jsonify({"message": "Application rejected!"})

@ngo_bp.route('/my-announcements', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_my_announcements():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    cur.execute("SELECT * FROM announcements WHERE ngo_id = ?", (ngo_id,))
    anns = []
    for row in cur.fetchall():
        d = dict(row)
        d['datePosted'] = d['created_at']
        anns.append(d)
    return jsonify(anns)

@ngo_bp.route('/announcements', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def create_announcement():
    data = request.json
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name FROM ngos WHERE user_id = ?", (request.user['id'],))
    ngo = cur.fetchone()
    if not ngo: return jsonify({"error": "NGO profile missing"}), 404
    
    cur.execute("INSERT INTO announcements (title, content, ngo_id, ngo_name) VALUES (?, ?, ?, ?)",
                (data.get('title'), data.get('content'), ngo['id'], ngo['name']))
    db.commit()
    
    cur.execute("SELECT id FROM users WHERE role='student'")
    for u in cur.fetchall():
        notify(u['id'], f"📢 Announcement from {ngo['name']}: \"{data.get('title')}\"", 'announcement')
    return jsonify({"message": "Announcement created"})

@ngo_bp.route('/announcements/<int:ann_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['ngo'])
def delete_announcement(ann_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    cur.execute("DELETE FROM announcements WHERE id=? AND ngo_id=?", (ann_id, ngo_id))
    db.commit()
    return jsonify({"message": "Deleted"})

@ngo_bp.route('/donation-requests', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_donations():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("SELECT * FROM book_donations WHERE ngo_id = ?", (ngo_id,))
    dons = []
    for row in cur.fetchall():
        d = dict(row)
        d['dateRequested'] = d['created_at']
        d['studentId'] = d['donor_id']
        d['bookId'] = d['id']
        dons.append(d)
    return jsonify(dons)

@ngo_bp.route('/donation-requests/<int:don_id>/accept', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def accept_donation(don_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE book_donations SET status='accepted' WHERE id=?", (don_id,))
    
    cur.execute("SELECT * FROM book_donations WHERE id=?", (don_id,))
    don = cur.fetchone()
    
    cur.execute("""
        INSERT INTO library_books (title, subject, condition, ngo_id, donor_id, donor_name, donation_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (don['book_title'], don['subject'], don['condition'], don['ngo_id'], don['donor_id'], don['donor_name'], don_id))
    db.commit()
    
    cur.execute("SELECT name FROM ngos WHERE id=?", (don['ngo_id'],))
    ngo = cur.fetchone()
    notify(don['donor_id'], f"✅ {ngo['name']} accepted your donation of \"{don['book_title']}\"! It's now in their library.", 'donation')
    return jsonify({"message": "Accepted"})

@ngo_bp.route('/donation-requests/<int:don_id>/reject', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def reject_donation(don_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE book_donations SET status='rejected' WHERE id=?", (don_id,))
    db.commit()
    
    cur.execute("SELECT * FROM book_donations WHERE id=?", (don_id,))
    don = cur.fetchone()
    cur.execute("SELECT name FROM ngos WHERE id=?", (don['ngo_id'],))
    ngo = cur.fetchone()
    notify(don['donor_id'], f"❌ {ngo['name']} could not accept your donation of \"{don['book_title']}\" at this time.", 'donation')
    return jsonify({"message": "Rejected"})

@ngo_bp.route('/library', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_library():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("SELECT * FROM library_books WHERE ngo_id = ?", (ngo_id,))
    # Also attach borrowedBy details
    books = []
    for row in cur.fetchall():
        b = dict(row)
        if b['status'] == 'borrowed':
            cur.execute("SELECT student_id, student_name, borrowed_at FROM borrow_requests WHERE book_id = ? AND status='approved'", (b['id'],))
            req = cur.fetchone()
            if req:
                b['borrowedBy'] = {'studentId': req['student_id'], 'studentName': req['student_name'], 'since': req['borrowed_at']}
        books.append(b)
    return jsonify(books)

@ngo_bp.route('/library/<int:book_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['ngo'])
def delete_book(book_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    cur.execute("DELETE FROM library_books WHERE id=? AND ngo_id=?", (book_id, ngo_id))
    db.commit()
    return jsonify({"message": "Deleted"})

@ngo_bp.route('/library/borrow-requests', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_borrow_reqs():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM ngos WHERE user_id = ?", (request.user['id'],))
    _ngo_row = cur.fetchone()
    if not _ngo_row: return jsonify([])
    ngo_id = _ngo_row['id']
    
    cur.execute("SELECT * FROM borrow_requests WHERE ngo_id = ? AND status='pending'", (ngo_id,))
    reqs = []
    for row in cur.fetchall():
        d = dict(row)
        d['bookTitle'] = d['book_title']
        d['studentName'] = d['student_name']
        reqs.append(d)
    return jsonify(reqs)

@ngo_bp.route('/library/borrow-requests/<int:req_id>/approve', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def approve_borrow(req_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE borrow_requests SET status='approved', borrowed_at=CURRENT_TIMESTAMP WHERE id=?", (req_id,))
    cur.execute("SELECT * FROM borrow_requests WHERE id=?", (req_id,))
    r = cur.fetchone()
    cur.execute("UPDATE library_books SET status='borrowed' WHERE id=?", (r['book_id'],))
    db.commit()
    
    cur.execute("SELECT name FROM ngos WHERE id=?", (r['ngo_id'],))
    ngo = cur.fetchone()
    notify(r['student_id'], f"📗 {ngo['name']} approved your request to borrow \"{r['book_title']}\". Please collect it soon!", 'borrow')
    return jsonify({"message": "Approved"})

@ngo_bp.route('/library/borrow-requests/<int:req_id>/reject', methods=['POST'])
@auth_middleware()
@role_middleware(['ngo'])
def reject_borrow(req_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE borrow_requests SET status='rejected' WHERE id=?", (req_id,))
    cur.execute("SELECT * FROM borrow_requests WHERE id=?", (req_id,))
    r = cur.fetchone()
    cur.execute("UPDATE library_books SET status='available' WHERE id=?", (r['book_id'],))
    db.commit()
    
    cur.execute("SELECT name FROM ngos WHERE id=?", (r['ngo_id'],))
    ngo = cur.fetchone()
    notify(r['student_id'], f"Your borrow request for \"{r['book_title']}\" was not approved by {ngo['name']}.", 'borrow')
    return jsonify({"message": "Rejected"})

@ngo_bp.route('/notifications', methods=['GET'])
@auth_middleware()
@role_middleware(['ngo'])
def get_notifications():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (request.user['id'],))
    notifs = []
    for row in cur.fetchall():
        d = dict(row)
        d['createdAt'] = d['created_at']
        notifs.append(d)
    return jsonify(notifs)

@ngo_bp.route('/notifications/read-all', methods=['PUT'])
@auth_middleware()
@role_middleware(['ngo'])
def read_all_notifications():
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (request.user['id'],))
    db.commit()
    return jsonify({"message": "All marked as read"})
