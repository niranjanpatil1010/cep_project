# Community Platform - Flask Edition

This is a newly converted version of the EduConnect platform, rebuilt using Python Flask, SQLite, and Vanilla JavaScript & HTML/CSS. Functionality remains identical to the original Node.js + React stack, but uses a much simpler, beginner-friendly architecture.

## Tech Stack
- **Backend:** Python + Flask
- **Database:** SQLite3 (Raw queries, no ORMs)
- **Frontend:** Flask Templates (HTML) + Plain CSS + Vanilla JS (Using fetch)

## Project Structure
- `app.py`: The main Flask server application that handles configuration, connects to the database, and exposes REST endpoints.
- `schema.sql`: Contains the definitions of all Database tables matching the entities.
- `init_db.py`: Setup script to create the DB tables and insert initial mock data.
- `routes/`: Blueprint endpoint files replacing the Express.js routes.
- `templates/`: Contains all HTML files (student dashboard, ngo dashboard, etc.).
- `static/css/`: Premium custom minimal CSS replacing Tailwind/CSS models.
- `static/js/`: Vanilla JS helper for standardizing API calls instead of Axios in React.

## How to Run Locally

### 1. Prerequisites
Ensure you have Python 3 installed on your system.

### 2. Install Requirements
Open a terminal in this folder (`flask_app`) and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database
Before running the application for the first time, you must initialize the SQLite database to create the necessary tables and populate some initial mock data.

```bash
python init_db.py
```
*(This will generate a `database.db` file in the folder).*

### 4. Start the Application
Run the Flask server:

```bash
python app.py
```

### 5. Open in browser
Navigate to `http://127.0.0.1:5000` in your web browser.

## Test Accounts (Created on Initialization)
- **Student:** `student1@test.com` / `password`
- **NGO Admin:** `ngo1@test.com` / `password`
- **Mentor:** `mentor1@test.com` / `password`
