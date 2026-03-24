import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_verification_email(email, token):
    # For demonstration, we'll just log it if mail is not configured
    # In a real app, use Flask-Mail
    verification_url = f"http://localhost:5000/api/auth/verify?token={token}"
    
    msg = MIMEText(f"Please verify your email by clicking here: {verification_url}")
    msg['Subject'] = "Verify your Email - EduConnect"
    msg['From'] = "no-reply@educonnect.com"
    msg['To'] = email

    print(f"DEBUG: Sending verification email to {email} with token {token}")
    print(f"DEBUG: Verification URL: {verification_url}")
    
    # Optional: Actual send logic if SMTP is configured
    # try:
    #     mail = current_app.extensions.get('mail')
    #     if mail:
    #         # Use Flask-Mail if available
    #         pass
    # except Exception as e:
    #     print(f"Error sending email: {e}")
