from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import psycopg2
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# ✅ Upload folder configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ PostgreSQL connection
conn = psycopg2.connect(
    dbname="complaint_db",
    user="postgres",
    password="1436",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# ✅ Create table with evidence_file column
try:
    cur.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            complaint TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            evidence_file TEXT
        )
    ''')
    conn.commit()
except Exception as e:
    conn.rollback()
    print("Table creation error:", e)

# ---------------- ROUTES ----------------

# ✅ Home Page
@app.route('/')
def index():
    try:
        conn.rollback()  # reset any previous error
        cur.execute("SELECT id, name, email, complaint, category, status, created_at FROM complaints")
        complaints = cur.fetchall()
        return render_template('index.html', complaints=complaints)
    except Exception as e:
        conn.rollback()
        return f"Database error: {e}"

# ✅ Submit Complaint
@app.route('/submit', methods=['POST'])
def submit():
    conn.rollback()  # 🔄 Reset transaction state
    name = request.form.get('name')
    email = request.form.get('email')
    complaint = request.form.get('complaint')
    category = request.form.get('category')
    file = request.files.get('evidence')

    filename = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if name and email and complaint and category:
        try:
            cur.execute(
                "INSERT INTO complaints (name, email, complaint, category, evidence_file) VALUES (%s, %s, %s, %s, %s)",
                (name, email, complaint, category, filename)
            )
            conn.commit()
            return redirect('/')
        except Exception as e:
            conn.rollback()
            return f"Database error: {e}", 500
    else:
        return "All fields are required", 400

# ✅ Admin Login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

# ✅ Admin Dashboard
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin')

    try:
        conn.rollback()
        if request.method == 'POST':
            complaint_id = request.form.get('complaint_id')
            if complaint_id:
                cur.execute("UPDATE complaints SET status='Resolved' WHERE id=%s", (complaint_id,))
                conn.commit()

        cur.execute("SELECT id, name, email, complaint, category, status, created_at, evidence_file FROM complaints")
        complaints = cur.fetchall()
        return render_template('admin_dashboard.html', complaints=complaints)
    except Exception as e:
        conn.rollback()
        return f"Dashboard Error: {e}"

# ✅ Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ✅ Admin Logout
@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')

# ---------------- END -------------------
# ✅ Check Status Page
@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    status_info = None
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        try:
            conn.rollback()
            cur.execute("SELECT * FROM complaints WHERE id = %s", (tracking_id,))
            status_info = cur.fetchone()
        except Exception as e:
            conn.rollback()
            return f"Database error: {e}"
    return render_template('check_status.html', status_info=status_info)
# ✅ Contact Us Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
