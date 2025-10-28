import os
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')  # change in production

DB_PATH = os.environ.get('DATABASE_PATH', 'patients.db')

# Helper: get DB connection (row factory as dict-like)
def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize SQLite database
def init_db():
    conn = get_db_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            condition TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Add Patient
@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        condition = request.form.get('condition', '').strip()
        if not name or not age or not condition:
            flash('Please fill all fields', 'error')
            return redirect(url_for('add_patient'))
        try:
            age_int = int(age)
        except ValueError:
            flash('Age must be a number', 'error')
            return redirect(url_for('add_patient'))

        conn = get_db_conn()
        conn.execute('INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)',
                     (name, age_int, condition))
        conn.commit()
        conn.close()
        flash('Patient added successfully', 'success')
        return redirect(url_for('view_patients'))
    return render_template('add_patient.html')

# View All Patients
@app.route('/patients')
def view_patients():
    conn = get_db_conn()
    cur = conn.execute('SELECT * FROM patients ORDER BY id DESC')
    patients = [dict(r) for r in cur.fetchall()]
    conn.close()
    return render_template('patients.html', patients=patients)

# Edit Patient
@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    conn = get_db_conn()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        condition = request.form.get('condition', '').strip()
        if not name or not age or not condition:
            flash('Please fill all fields', 'error')
            conn.close()
            return redirect(url_for('edit_patient', patient_id=patient_id))
        try:
            age_int = int(age)
        except ValueError:
            flash('Age must be a number', 'error')
            conn.close()
            return redirect(url_for('edit_patient', patient_id=patient_id))

        conn.execute('UPDATE patients SET name=?, age=?, condition=? WHERE id=?',
                     (name, age_int, condition, patient_id))
        conn.commit()
        conn.close()
        flash('Patient updated successfully', 'success')
        return redirect(url_for('view_patients'))

    cur = conn.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient_row = cur.fetchone()
    conn.close()
    if not patient_row:
        flash('Patient not found', 'error')
        return redirect(url_for('view_patients'))
    patient = dict(patient_row)
    return render_template('edit_patient.html', patient=patient)

# Search Patient
@app.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        name = request.form.get('search_name', '').strip()
        conn = get_db_conn()
        cur = conn.execute('SELECT * FROM patients WHERE name LIKE ?', ('%' + name + '%',))
        results = [dict(r) for r in cur.fetchall()]
        conn.close()
        return render_template('search_results.html', results=results, query=name)
    return render_template('search.html')

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    conn = get_db_conn()
    conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
    flash('Patient deleted', 'success')
    return redirect(url_for('view_patients'))

if __name__ == '__main__':
    init_db()  # Create database on first run
    # In development you can keep debug=True; remove for production
    app.run(debug=True, host='0.0.0.0')