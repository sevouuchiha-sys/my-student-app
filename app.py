import os
import psycopg2
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# --- DATABASE CONNECTION (PostgreSQL) ---
def get_db_connection():
    # Kukunin nito ang "Internal Database URL" mula sa Render settings mamaya
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            grade INTEGER,
            section TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Subukan i-initialize ang DB pagtakbo ng app
try:
    init_db()
except:
    print("Database not ready yet...")

# --- HTML UI (Same as before) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Permanent Student CRUD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #eef2f3; padding-top: 50px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .btn-primary { background: #007bff; border: none; }
    </style>
</head>
<body>
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-9">
            <div class="card p-4">
                <h3 class="text-center mb-4">Student Database (PostgreSQL)</h3>
                <div class="row g-2 mb-4">
                    <input type="hidden" id="student-id">
                    <div class="col-md-5"><input type="text" id="name" class="form-control" placeholder="Student Name"></div>
                    <div class="col-md-2"><input type="number" id="grade" class="form-control" placeholder="Grade"></div>
                    <div class="col-md-3"><input type="text" id="section" class="form-control" placeholder="Section"></div>
                    <div class="col-md-2"><button class="btn btn-primary w-100" onclick="saveStudent()" id="btn-text">Add</button></div>
                </div>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead class="table-light"><tr><th>Name</th><th>Grade</th><th>Section</th><th>Actions</th></tr></thead>
                        <tbody id="student-list"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    const API = '/students';
    async function load() {
        const res = await fetch(API);
        const data = await res.json();
        document.getElementById('student-list').innerHTML = data.students.map(s => `
            <tr>
                <td><b>${s.name}</b></td><td>${s.grade}</td><td>${s.section}</td>
                <td>
                    <button class="btn btn-sm btn-info text-white me-1" onclick='editStudent(${JSON.stringify(s)})'>Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            </tr>`).join('');
    }
    async function saveStudent() {
        const id = document.getElementById('student-id').value;
        const data = { name: document.getElementById('name').value, grade: document.getElementById('grade').value, section: document.getElementById('section').value };
        await fetch(id ? `${API}/${id}` : API, { method: id ? 'PUT' : 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
        reset(); load();
    }
    async function deleteStudent(id) { if(confirm("Delete this?")) { await fetch(`${API}/${id}`, { method: 'DELETE' }); load(); } }
    function editStudent(s) { document.getElementById('student-id').value = s.id; document.getElementById('name').value = s.name; document.getElementById('grade').value = s.grade; document.getElementById('section').value = s.section; document.getElementById('btn-text').innerText = "Update"; }
    function reset() { document.getElementById('student-id').value = ''; document.getElementById('name').value = ''; document.getElementById('grade').value = ''; document.getElementById('section').value = ''; document.getElementById('btn-text').innerText = "Add"; }
    load();
</script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_UI)

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM students ORDER BY id ASC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({"students": [{"id": r[0], "name": r[1], "grade": r[2], "section": r[3]} for r in rows]})

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO students (name, grade, section) VALUES (%s, %s, %s)',
                (data.get('name'), data.get('grade'), data.get('section')))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE students SET name=%s, grade=%s, section=%s WHERE id=%s',
                (data.get('name'), data.get('grade'), data.get('section'), id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "updated"})

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM students WHERE id=%s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
