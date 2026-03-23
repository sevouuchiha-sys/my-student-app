import os
import sqlite3
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
DB_NAME = 'database.db'

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade INTEGER,
                section TEXT
            )
        ''')
        conn.commit()

init_db()

# --- HTML & CSS UI (Embedded) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student CRUD - Chromebook Edition</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #f4f7f6; padding-top: 50px; }
        .main-card { border: none; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .btn-primary { background: #4e73df; border: none; }
    </style>
</head>
<body>
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-10">
            <div class="card main-card p-4">
                <h3 class="text-center mb-4 text-primary">Student Management System</h3>
                
                <div class="row g-3 mb-4">
                    <input type="hidden" id="student-id">
                    <div class="col-md-4">
                        <input type="text" id="name" class="form-control" placeholder="Student Name">
                    </div>
                    <div class="col-md-3">
                        <input type="number" id="grade" class="form-control" placeholder="Grade">
                    </div>
                    <div class="col-md-3">
                        <input type="text" id="section" class="form-control" placeholder="Section">
                    </div>
                    <div class="col-md-2">
                        <button class="btn btn-primary w-100" onclick="saveStudent()" id="btn-text">Add</button>
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table table-hover align-middle">
                        <thead class="table-light">
                            <tr>
                                <th>Name</th><th>Grade</th><th>Section</th><th class="text-center">Actions</th>
                            </tr>
                        </thead>
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
        const list = document.getElementById('student-list');
        list.innerHTML = data.students.map(s => `
            <tr>
                <td><b>${s.name}</b></td>
                <td>${s.grade}</td>
                <td>${s.section}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-info me-2" onclick='editStudent(${JSON.stringify(s)})'>Edit</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            </tr>`).join('');
    }

    async function saveStudent() {
        const id = document.getElementById('student-id').value;
        const data = {
            name: document.getElementById('name').value,
            grade: document.getElementById('grade').value,
            section: document.getElementById('section').value
        };
        if(!data.name) return alert("Paki-lagay ang pangalan.");
        
        await fetch(id ? `${API}/${id}` : API, {
            method: id ? 'PUT' : 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        reset(); load();
    }

    async function deleteStudent(id) {
        if(confirm("Sigurado ka bang buburahin ito?")) {
            await fetch(`${API}/${id}`, { method: 'DELETE' });
            load();
        }
    }

    function editStudent(s) {
        document.getElementById('student-id').value = s.id;
        document.getElementById('name').value = s.name;
        document.getElementById('grade').value = s.grade;
        document.getElementById('section').value = s.section;
        document.getElementById('btn-text').innerText = "Update";
    }

    function reset() {
        document.getElementById('student-id').value = '';
        document.getElementById('name').value = '';
        document.getElementById('grade').value = '';
        document.getElementById('section').value = '';
        document.getElementById('btn-text').innerText = "Add";
    }
    load();
</script>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def home():
    return render_template_string(HTML_UI)

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify({"students": [dict(row) for row in rows]})

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.execute('INSERT INTO students (name, grade, section) VALUES (?, ?, ?)',
                       (data.get('name'), data.get('grade'), data.get('section')))
    conn.commit()
    conn.close()
    return jsonify({"id": cur.lastrowid}), 201

@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE students SET name = ?, grade = ?, section = ? WHERE id = ?',
                 (data.get('name'), data.get('grade'), data.get('section'), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
