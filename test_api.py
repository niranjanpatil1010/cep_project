import sqlite3
import urllib.request
import urllib.error
import json

db_path = r"c:\Users\niranjan patil\Desktop\sem4\cep_project\flask_app\database.db"
base_url = "http://localhost:5000/api/ngo"
endpoints = [
    '/analytics',
    '/my-scholarships',
    '/applications',
    '/my-events',
    '/donation-requests',
    '/library',
    '/library/borrow-requests',
    '/my-announcements',
    '/notifications'
]

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT id, name, email FROM users WHERE role='ngo'")
ngos = cur.fetchall()

print(f"Found {len(ngos)} NGOs in database.")

for ngo in ngos:
    uid = ngo[0]
    name = ngo[1]
    print(f"\n--- Testing NGO: {name} (User ID: {uid}) ---")
    token = f"fake-jwt-token-{uid}"
    
    for ep in endpoints:
        url = base_url + ep
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req) as response:
                pass # success
                # print(f"{ep}: 200 OK")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"CRASH -> {ep}: HTTP {e.code}")
            if "Total Applications" in body or "500 Internal Server" in body or True:
                print(f"Body snippet: {body[:200]}")
        except Exception as e:
            print(f"CRASH -> {ep}: ERROR {e}")
