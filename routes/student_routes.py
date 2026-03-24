from flask import Blueprint, request, jsonify
from middleware import auth_middleware, role_middleware, notify
from db import get_db

student_bp = Blueprint('student', __name__)

@student_bp.route('/ngos', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_ngos():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM ngos")
    return jsonify([dict(row) for row in cur.fetchall()])

@student_bp.route('/scholarships', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_scholarships():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM scholarships")
    return jsonify([dict(row) for row in cur.fetchall()])

@student_bp.route('/scholarships/<int:scholarship_id>/apply', methods=['POST'])
@auth_middleware()
@role_middleware(['student'])
def apply_scholarship(scholarship_id):
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
    scholarship = cur.fetchone()
    if not scholarship:
        return jsonify({'message': 'Scholarship not found'}), 404
        
    cur.execute("SELECT * FROM applications WHERE scholarship_id = ? AND student_id = ?", (scholarship_id, request.user['id']))
    if cur.fetchone():
        return jsonify({'message': 'Already applied for this scholarship'}), 409
        
    data = request.json
    
    cur.execute("""
        INSERT INTO applications (scholarship_id, student_id, applicant_name, applicant_email, applicant_phone, applicant_education, applicant_gpa, applicant_sop)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (scholarship_id, request.user['id'], data.get('fullName', request.user['name']), data.get('email', ''), 
          data.get('phone', ''), data.get('educationLevel', ''), data.get('gpa', ''), data.get('statementOfPurpose', '')))
    app_id = cur.lastrowid
    
    cur.execute("SELECT user_id, name FROM ngos WHERE id = ?", (scholarship['ngo_id'],))
    ngo = cur.fetchone()
    if ngo:
        notify(ngo['user_id'], f"📋 New application for \"{scholarship['title']}\" from {data.get('fullName', request.user['name'])}", 'application')
        
    cur.execute("INSERT INTO student_activity_history (student_id, action, details) VALUES (?, ?, ?)",
                (request.user['id'], 'scholarship_application', f"Applied for: {scholarship['title']}"))
    
    db.commit()
    
    cur.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    new_app = dict(cur.fetchone())
    return jsonify({'message': 'Application submitted successfully!', 'application': new_app}), 201

@student_bp.route('/scholarship-applications/<int:app_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['student'])
def cancel_application(app_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM applications WHERE id = ? AND student_id = ?", (app_id, request.user['id']))
    if not cur.fetchone():
        return jsonify({'message': 'Application not found'}), 404
    cur.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    db.commit()
    return jsonify({'message': 'Application cancelled'}), 200

@student_bp.route('/events', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_events():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM events")
    return jsonify([dict(row) for row in cur.fetchall()])

@student_bp.route('/events/<int:event_id>/register', methods=['POST'])
@auth_middleware()
@role_middleware(['student'])
def register_event(event_id):
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cur.fetchone()
    if not event:
        return jsonify({'message': 'Event not found'}), 404
        
    cur.execute("SELECT * FROM event_registrations WHERE event_id = ? AND student_id = ?", (event_id, request.user['id']))
    if cur.fetchone():
        return jsonify({'message': 'Already registered for this event'}), 409
        
    cur.execute("INSERT INTO event_registrations (event_id, student_id, student_name, student_email) VALUES (?, ?, ?, ?)",
                (event_id, request.user['id'], request.user['name'], request.user['email']))
    reg_id = cur.lastrowid
    
    cur.execute("SELECT user_id, name FROM ngos WHERE id = ?", (event['ngo_id'],))
    ngo = cur.fetchone()
    if ngo:
        notify(ngo['user_id'], f"🎟️ {request.user['name']} registered for your event: \"{event['title']}\"", 'event')
        
    cur.execute("INSERT INTO student_activity_history (student_id, action, details) VALUES (?, ?, ?)",
                (request.user['id'], 'event_registration', f"Registered for event: {event['title']}"))
    db.commit()
    
    cur.execute("SELECT * FROM event_registrations WHERE id = ?", (reg_id,))
    return jsonify({'message': 'Registered successfully!', 'registration': dict(cur.fetchone())}), 201

@student_bp.route('/event-registrations/<int:reg_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['student'])
def cancel_registration(reg_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM event_registrations WHERE id = ? AND student_id = ?", (reg_id, request.user['id']))
    if not cur.fetchone():
        return jsonify({'message': 'Registration not found'}), 404
    cur.execute("DELETE FROM event_registrations WHERE id = ?", (reg_id,))
    db.commit()
    return jsonify({'message': 'Registration cancelled'}), 200

@student_bp.route('/books/donate', methods=['POST'])
@auth_middleware()
@role_middleware(['student'])
def donate_book():
    data = request.json
    db = get_db()
    cur = db.cursor()
    
    if not all([data.get('title'), data.get('subject'), data.get('condition'), data.get('location'), data.get('ngoId')]):
        return jsonify({'message': 'All fields including NGO selection are required'}), 400
        
    ngo_id = int(data.get('ngoId'))
    cur.execute("SELECT * FROM ngos WHERE id = ?", (ngo_id,))
    ngo = cur.fetchone()
    if not ngo:
        return jsonify({'message': 'NGO not found'}), 404
        
    cur.execute("""
        INSERT INTO book_donations (book_title, subject, condition, location, donor_id, donor_name, ngo_id, ngo_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['title'], data['subject'], data['condition'], data['location'], request.user['id'], request.user['name'], ngo_id, ngo['name']))
    don_id = cur.lastrowid
    
    notify(ngo['user_id'], f"📚 {request.user['name']} wants to donate \"{data['title']}\" to your library", 'donation')
    cur.execute("INSERT INTO student_activity_history (student_id, action, details) VALUES (?, ?, ?)",
                (request.user['id'], 'book_donation', f"Donated book \"{data['title']}\" to {ngo['name']}"))
    db.commit()
    
    cur.execute("SELECT * FROM book_donations WHERE id = ?", (don_id,))
    return jsonify({'message': 'Donation request submitted!', 'donation': dict(cur.fetchone())}), 201

@student_bp.route('/my-donations', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def my_donations():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM book_donations WHERE donor_id = ?", (request.user['id'],))
    
    # Needs mapping 'book_title' to 'title' 
    donations = []
    for row in cur.fetchall():
        d = dict(row)
        d['title'] = d['book_title']
        d['ngoName'] = d['ngo_name']
        donations.append(d)
    return jsonify(donations)

@student_bp.route('/my-donations/<int:don_id>', methods=['DELETE'])
@auth_middleware()
@role_middleware(['student'])
def cancel_donation(don_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM book_donations WHERE id = ? AND donor_id = ? AND status = 'pending'", (don_id, request.user['id']))
    if not cur.fetchone():
        return jsonify({'message': 'Donation not found or already processed'}), 404
    cur.execute("DELETE FROM book_donations WHERE id = ?", (don_id,))
    db.commit()
    return jsonify({'message': 'Donation request cancelled'}), 200

@student_bp.route('/library', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_all_library():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT l.*, n.name as ngoName 
        FROM library_books l
        LEFT JOIN ngos n ON l.ngo_id = n.id
    """)
    return jsonify([dict(row) for row in cur.fetchall()])

@student_bp.route('/library/<int:ngo_id>', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_ngo_library(ngo_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT l.*, n.name as ngoName 
        FROM library_books l
        LEFT JOIN ngos n ON l.ngo_id = n.id
        WHERE l.ngo_id = ?
    """, (ngo_id,))
    return jsonify([dict(row) for row in cur.fetchall()])

@student_bp.route('/library/<int:book_id>/borrow', methods=['POST'])
@auth_middleware()
@role_middleware(['student'])
def borrow_request(book_id):
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT * FROM library_books WHERE id = ?", (book_id,))
    book = cur.fetchone()
    if not book:
        return jsonify({'message': 'Book not found'}), 404
    if book['status'] != 'available':
        return jsonify({'message': 'Book is not available for borrowing'}), 409
        
    cur.execute("SELECT * FROM borrow_requests WHERE book_id = ? AND student_id = ? AND status = 'pending'", (book_id, request.user['id']))
    if cur.fetchone():
        return jsonify({'message': 'Already requested this book'}), 409
        
    cur.execute("""
        INSERT INTO borrow_requests (book_id, book_title, student_id, student_name, student_email, ngo_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, book['title'], request.user['id'], request.user['name'], request.user['email'], book['ngo_id']))
    req_id = cur.lastrowid
    
    cur.execute("UPDATE library_books SET status = 'requested' WHERE id = ?", (book_id,))
    
    cur.execute("SELECT user_id, name FROM ngos WHERE id = ?", (book['ngo_id'],))
    ngo = cur.fetchone()
    if ngo:
        notify(ngo['user_id'], f"📖 {request.user['name']} wants to borrow \"{book['title']}\" from your library", 'borrow')
        
    db.commit()
    
    cur.execute("SELECT * FROM borrow_requests WHERE id = ?", (req_id,))
    return jsonify({'message': 'Borrow request submitted!', 'request': dict(cur.fetchone())}), 201

@student_bp.route('/library/borrows/<int:req_id>/return', methods=['POST'])
@auth_middleware()
@role_middleware(['student'])
def return_book(req_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM borrow_requests WHERE id = ? AND student_id = ? AND status = 'approved'", (req_id, request.user['id']))
    borrow_req = cur.fetchone()
    if not borrow_req:
        return jsonify({'message': 'Borrow record not found'}), 404
        
    cur.execute("UPDATE borrow_requests SET status = 'returned', returned_at = CURRENT_TIMESTAMP WHERE id = ?", (req_id,))
    cur.execute("UPDATE library_books SET status = 'available' WHERE id = ?", (borrow_req['book_id'],))
    
    cur.execute("SELECT user_id, name FROM ngos WHERE id = ?", (borrow_req['ngo_id'],))
    ngo = cur.fetchone()
    if ngo:
        notify(ngo['user_id'], f"✅ \"{borrow_req['book_title']}\" has been returned to your library", 'borrow')
        
    db.commit()
    return jsonify({'message': 'Book returned successfully!'}), 200

@student_bp.route('/my-borrows', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def my_borrows():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM borrow_requests WHERE student_id = ?", (request.user['id'],))
    
    borrows = []
    for row in cur.fetchall():
        d = dict(row)
        d['bookTitle'] = d['book_title']
        d['requestedAt'] = d['requested_at']
        d['borrowedAt'] = d['borrowed_at']
        borrows.append(d)
    return jsonify(borrows)

@student_bp.route('/mentor-posts', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_mentor_posts():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM mentor_posts")
    posts = []
    for row in cur.fetchall():
        d = dict(row)
        if d.get('tags'):
            d['tags'] = d['tags'].split(',')
        else:
            d['tags'] = []
        posts.append(d)
    return jsonify(posts)

@student_bp.route('/announcements', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_announcements():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM announcements")
    anns = []
    for row in cur.fetchall():
        d = dict(row)
        d['ngoName'] = d['ngo_name']
        d['datePosted'] = d['created_at']
        anns.append(d)
    return jsonify(anns)

@student_bp.route('/history', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
def get_history():
    db = get_db()
    cur = db.cursor()
    student_id = request.user['id']
    
    cur.execute("SELECT * FROM applications WHERE student_id = ?", (student_id,))
    apps = []
    for row in cur.fetchall():
        d = dict(row)
        d['scholarshipId'] = d['scholarship_id']
        d['dateApplied'] = d['applied_at']
        apps.append(d)
        
    cur.execute("SELECT * FROM event_registrations WHERE student_id = ?", (student_id,))
    events = []
    for row in cur.fetchall():
        d = dict(row)
        d['eventId'] = d['event_id']
        events.append(d)
        
    cur.execute("SELECT * FROM book_donations WHERE donor_id = ?", (student_id,))
    dons = []
    for row in cur.fetchall():
        d = dict(row)
        d['title'] = d['book_title']
        d['ngoName'] = d['ngo_name']
        d['createdAt'] = d['created_at']
        dons.append(d)
        
    cur.execute("SELECT * FROM borrow_requests WHERE student_id = ?", (student_id,))
    borrows = []
    for row in cur.fetchall():
        d = dict(row)
        d['bookTitle'] = d['book_title']
        d['requestedAt'] = d['requested_at']
        d['borrowedAt'] = d['borrowed_at']
        borrows.append(d)
        
    return jsonify({
        'scholarshipApps': apps,
        'registeredEvents': events,
        'myDonations': dons,
        'myBorrows': borrows
    })

@student_bp.route('/notifications', methods=['GET'])
@auth_middleware()
@role_middleware(['student'])
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

@student_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
@auth_middleware()
@role_middleware(['student'])
def read_notification(notif_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE notifications SET read = 1 WHERE id = ? AND user_id = ?", (notif_id, request.user['id']))
    db.commit()
    return jsonify({"message": "Marked as read"})

@student_bp.route('/notifications/read-all', methods=['PUT'])
@auth_middleware()
@role_middleware(['student'])
def read_all_notifications():
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (request.user['id'],))
    db.commit()
    return jsonify({"message": "All marked as read"})
