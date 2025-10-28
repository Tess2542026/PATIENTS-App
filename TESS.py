from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('patients.db')
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
        name = request.form['name']
        age = request.form['age']
        condition = request.form['condition']
        conn = sqlite3.connect('patients.db')
        conn.execute('INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)', (name, age, condition))
        conn.commit()
        conn.close()
        return redirect(url_for('view_patients'))
    return render_template('add_patient.html')

# View All Patients
@app.route('/patients')
def view_patients():
    conn = sqlite3.connect('patients.db')
    # return rows as mappings so templates can access by column name
    conn.row_factory = sqlite3.Row
    cur = conn.execute('SELECT * FROM patients')
    patients = [dict(r) for r in cur.fetchall()]
    conn.close()
    return render_template('patients.html', patients=patients)

# Search Patient
@app.route('/search', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        name = request.form['search_name']
        conn = sqlite3.connect('patients.db')
        conn.row_factory = sqlite3.Row
        cur = conn.execute('SELECT * FROM patients WHERE name LIKE ?', ('%' + name + '%',))
        results = [dict(r) for r in cur.fetchall()]
        conn.close()
        return render_template('search_results.html', results=results)
    return render_template('search.html')


@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    conn = sqlite3.connect('patients.db')
    conn.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_patients'))

if __name__ == '__main__':
    init_db()  # Create database on first run
    app.run(debug=True)












        

