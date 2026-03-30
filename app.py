import os
import psycopg2
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# --- DATABASE CONNECTION (PostgreSQL) ---
def get_db_connection():
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

try:
    init_db()
except:
    print("Database not ready yet...")

# --- ENHANCED HTML UI ---
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Database</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0a0e17;
            --bg-card: #111827;
            --bg-card-hover: #1a2236;
            --bg-input: #0d1321;
            --border: #1e293b;
            --border-focus: #10b981;
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.25);
            --accent-hover: #34d399;
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.25);
            --warning: #f59e0b;
            --info: #06b6d4;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #475569;
        }

        * { box-sizing: border-box; }

        body {
            background: var(--bg-deep);
            color: var(--text-primary);
            font-family: 'Space Grotesk', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Animated background */
        .bg-layer {
            position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
        }
        .bg-orb {
            position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.15;
            animation: orbFloat 20s ease-in-out infinite;
        }
        .bg-orb:nth-child(1) {
            width: 600px; height: 600px; background: #10b981;
            top: -200px; left: -100px; animation-delay: 0s;
        }
        .bg-orb:nth-child(2) {
            width: 500px; height: 500px; background: #06b6d4;
            bottom: -150px; right: -100px; animation-delay: -7s;
            animation-duration: 25s;
        }
        .bg-orb:nth-child(3) {
            width: 350px; height: 350px; background: #f59e0b;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
            animation-delay: -14s; animation-duration: 30s; opacity: 0.08;
        }
        @keyframes orbFloat {
            0%, 100% { transform: translate(0, 0) scale(1); }
            25% { transform: translate(60px, -40px) scale(1.1); }
            50% { transform: translate(-30px, 60px) scale(0.95); }
            75% { transform: translate(40px, 30px) scale(1.05); }
        }

        /* Grid pattern overlay */
        .bg-grid {
            position: fixed; inset: 0; z-index: 0; pointer-events: none;
            background-image:
                linear-gradient(rgba(16,185,129,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(16,185,129,0.03) 1px, transparent 1px);
            background-size: 60px 60px;
        }

        .main-wrapper {
            position: relative; z-index: 1;
            padding: 40px 16px 80px;
        }

        /* Header */
        .page-header {
            text-align: center; margin-bottom: 36px;
            animation: fadeSlideDown 0.8s ease-out;
        }
        .page-header .badge-label {
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25);
            color: var(--accent); font-size: 12px; font-weight: 500;
            padding: 5px 14px; border-radius: 50px; margin-bottom: 16px;
            letter-spacing: 0.5px; text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
        }
        .page-header .badge-label i { font-size: 10px; }
        .page-header h1 {
            font-size: clamp(28px, 5vw, 42px); font-weight: 700;
            letter-spacing: -1px; line-height: 1.15; margin-bottom: 8px;
        }
        .page-header h1 span { color: var(--accent); }
        .page-header p { color: var(--text-secondary); font-size: 15px; max-width: 460px; margin: 0 auto; }

        @keyframes fadeSlideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Stats row */
        .stats-row {
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
            margin-bottom: 28px; animation: fadeSlideUp 0.8s ease-out 0.1s both;
        }
        .stat-card {
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 14px; padding: 20px; text-align: center;
            transition: all 0.3s ease; position: relative; overflow: hidden;
        }
        .stat-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            opacity: 0; transition: opacity 0.3s ease;
        }
        .stat-card:hover { border-color: rgba(16,185,129,0.3); transform: translateY(-2px); }
        .stat-card:hover::before { opacity: 1; }
        .stat-card .stat-icon {
            width: 40px; height: 40px; border-radius: 10px; display: inline-flex;
            align-items: center; justify-content: center; font-size: 16px;
            margin-bottom: 10px;
        }
        .stat-card:nth-child(1) .stat-icon { background: rgba(16,185,129,0.12); color: var(--accent); }
        .stat-card:nth-child(2) .stat-icon { background: rgba(6,182,212,0.12); color: var(--info); }
        .stat-card:nth-child(3) .stat-icon { background: rgba(245,158,11,0.12); color: var(--warning); }
        .stat-card .stat-number {
            font-size: 28px; font-weight: 700; line-height: 1; margin-bottom: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        .stat-card .stat-label { color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }

        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Main card */
        .main-card {
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 18px; overflow: hidden;
            animation: fadeSlideUp 0.8s ease-out 0.2s both;
            box-shadow: 0 8px 40px rgba(0,0,0,0.3);
        }

        /* Form section */
        .form-section {
            padding: 28px 28px 24px; border-bottom: 1px solid var(--border);
            background: linear-gradient(180deg, rgba(16,185,129,0.02) 0%, transparent 100%);
        }
        .form-section .form-label-custom {
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
            color: var(--text-muted); margin-bottom: 6px; font-weight: 500;
        }
        .form-control-custom {
            background: var(--bg-input); border: 1px solid var(--border);
            color: var(--text-primary); border-radius: 10px; padding: 10px 14px;
            font-size: 14px; font-family: 'Space Grotesk', sans-serif;
            transition: all 0.25s ease; width: 100%;
        }
        .form-control-custom::placeholder { color: var(--text-muted); }
        .form-control-custom:focus {
            outline: none; border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
            background: rgba(16,185,129,0.03);
        }

        .btn-add {
            background: linear-gradient(135deg, #10b981, #059669);
            border: none; color: #fff; border-radius: 10px; padding: 10px 24px;
            font-weight: 600; font-size: 14px; cursor: pointer;
            transition: all 0.25s ease; font-family: 'Space Grotesk', sans-serif;
            display: inline-flex; align-items: center; gap: 8px; height: 100%;
            min-width: 120px; justify-content: center;
        }
        .btn-add:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(16,185,129,0.35);
        }
        .btn-add:active { transform: translateY(0); }
        .btn-add.updating {
            background: linear-gradient(135deg, #06b6d4, #0891b2);
        }
        .btn-add.updating:hover {
            box-shadow: 0 6px 20px rgba(6,182,212,0.35);
        }

        /* Table section */
        .table-section { padding: 0; }
        .table-toolbar {
            padding: 20px 28px 16px; display: flex; align-items: center;
            justify-content: space-between; gap: 16px; flex-wrap: wrap;
        }
        .table-toolbar h2 {
            font-size: 16px; font-weight: 600; margin: 0;
            display: flex; align-items: center; gap: 10px;
        }
        .table-toolbar h2 .count-badge {
            background: rgba(16,185,129,0.12); color: var(--accent);
            font-size: 12px; padding: 2px 10px; border-radius: 50px;
            font-family: 'JetBrains Mono', monospace;
        }
        .search-box {
            position: relative; flex: 0 0 280px; max-width: 100%;
        }
        .search-box i {
            position: absolute; left: 14px; top: 50%; transform: translateY(-50%);
            color: var(--text-muted); font-size: 13px;
        }
        .search-box input {
            background: var(--bg-input); border: 1px solid var(--border);
            color: var(--text-primary); border-radius: 10px; padding: 8px 14px 8px 38px;
            font-size: 13px; font-family: 'Space Grotesk', sans-serif;
            transition: all 0.25s ease; width: 100%;
        }
        .search-box input:focus {
            outline: none; border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        .search-box input::placeholder { color: var(--text-muted); }

        .table-wrap { overflow-x: auto; }
        .table-custom {
            width: 100%; border-collapse: separate; border-spacing: 0;
        }
        .table-custom thead th {
            background: rgba(16,185,129,0.04); color: var(--text-muted);
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;
            font-weight: 600; padding: 12px 28px; border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }
        .table-custom tbody tr {
            transition: all 0.2s ease;
        }
        .table-custom tbody tr:hover { background: var(--bg-card-hover); }
        .table-custom tbody td {
            padding: 14px 28px; border-bottom: 1px solid rgba(30,41,59,0.5);
            vertical-align: middle; font-size: 14px;
        }
        .table-custom tbody tr:last-child td { border-bottom: none; }

        .student-name {
            font-weight: 600; color: var(--text-primary);
            display: flex; align-items: center; gap: 10px;
        }
        .student-avatar {
            width: 32px; height: 32px; border-radius: 8px; display: flex;
            align-items: center; justify-content: center; font-size: 13px;
            font-weight: 700; color: #fff; flex-shrink: 0;
        }
        .grade-badge {
            display: inline-flex; align-items: center; gap: 4px;
            background: rgba(6,182,212,0.1); color: var(--info);
            padding: 3px 10px; border-radius: 6px; font-size: 13px;
            font-family: 'JetBrains Mono', monospace; font-weight: 500;
        }
        .section-tag {
            background: rgba(245,158,11,0.1); color: var(--warning);
            padding: 3px 10px; border-radius: 6px; font-size: 13px; font-weight: 500;
        }
        .action-btns { display: flex; gap: 6px; }
        .btn-icon {
            width: 34px; height: 34px; border-radius: 8px; border: 1px solid var(--border);
            background: transparent; color: var(--text-secondary); cursor: pointer;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 13px; transition: all 0.2s ease;
        }
        .btn-icon.edit:hover {
            background: rgba(6,182,212,0.12); border-color: rgba(6,182,212,0.3);
            color: var(--info); transform: translateY(-1px);
        }
        .btn-icon.delete:hover {
            background: rgba(239,68,68,0.12); border-color: rgba(239,68,68,0.3);
            color: var(--danger); transform: translateY(-1px);
        }

        /* Empty state */
        .empty-state {
            text-align: center; padding: 60px 20px; color: var(--text-muted);
        }
        .empty-state i { font-size: 48px; margin-bottom: 16px; opacity: 0.3; }
        .empty-state p { font-size: 14px; margin: 0; }

        /* Toast */
        .toast-container {
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            display: flex; flex-direction: column; gap: 8px;
        }
        .toast-msg {
            background: var(--bg-card); border: 1px solid var(--border);
            color: var(--text-primary); padding: 12px 20px; border-radius: 12px;
            font-size: 13px; display: flex; align-items: center; gap: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            animation: toastIn 0.35s ease-out;
            min-width: 250px;
        }
        .toast-msg.success { border-left: 3px solid var(--accent); }
        .toast-msg.success i { color: var(--accent); }
        .toast-msg.danger { border-left: 3px solid var(--danger); }
        .toast-msg.danger i { color: var(--danger); }
        .toast-msg.info { border-left: 3px solid var(--info); }
        .toast-msg.info i { color: var(--info); }
        .toast-msg.leaving { animation: toastOut 0.3s ease-in forwards; }
        @keyframes toastIn {
            from { opacity: 0; transform: translateX(40px) scale(0.95); }
            to { opacity: 1; transform: translateX(0) scale(1); }
        }
        @keyframes toastOut {
            to { opacity: 0; transform: translateX(40px) scale(0.95); }
        }

        /* Row animations */
        .row-enter {
            animation: rowSlideIn 0.35s ease-out;
        }
        @keyframes rowSlideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .row-exit {
            animation: rowSlideOut 0.3s ease-in forwards;
        }
        @keyframes rowSlideOut {
            to { opacity: 0; transform: translateX(30px); height: 0; padding: 0; overflow: hidden; }
        }

        /* Confirm modal */
        .modal-overlay {
            position: fixed; inset: 0; z-index: 9998; background: rgba(0,0,0,0.6);
            backdrop-filter: blur(4px); display: flex; align-items: center;
            justify-content: center; animation: fadeIn 0.2s ease;
        }
        .modal-box {
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 16px; padding: 28px; max-width: 380px; width: 90%;
            text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            animation: modalPop 0.3s ease-out;
        }
        .modal-box .modal-icon {
            width: 52px; height: 52px; border-radius: 50%; margin: 0 auto 16px;
            display: flex; align-items: center; justify-content: center;
            background: var(--danger-glow); color: var(--danger); font-size: 22px;
        }
        .modal-box h3 { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
        .modal-box p { color: var(--text-secondary); font-size: 14px; margin-bottom: 24px; }
        .modal-box .modal-btns { display: flex; gap: 10px; justify-content: center; }
        .modal-box .btn-cancel {
            background: var(--bg-input); border: 1px solid var(--border); color: var(--text-secondary);
            border-radius: 10px; padding: 9px 20px; font-size: 13px; cursor: pointer;
            font-family: 'Space Grotesk', sans-serif; font-weight: 500;
            transition: all 0.2s ease;
        }
        .modal-box .btn-cancel:hover { border-color: var(--text-muted); color: var(--text-primary); }
        .modal-box .btn-delete {
            background: var(--danger); border: none; color: #fff;
            border-radius: 10px; padding: 9px 20px; font-size: 13px; cursor: pointer;
            font-family: 'Space Grotesk', sans-serif; font-weight: 600;
            transition: all 0.2s ease;
        }
        .modal-box .btn-delete:hover { box-shadow: 0 4px 16px var(--danger-glow); transform: translateY(-1px); }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes modalPop {
            from { opacity: 0; transform: scale(0.9) translateY(10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        /* Loading spinner */
        .spinner {
            width: 18px; height: 18px; border: 2px solid transparent;
            border-top-color: #fff; border-radius: 50%;
            animation: spin 0.6s linear infinite; display: none;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* Responsive */
        @media (max-width: 768px) {
            .stats-row { grid-template-columns: 1fr; }
            .form-section { padding: 20px 18px 18px; }
            .table-toolbar { padding: 16px 18px 12px; flex-direction: column; align-items: stretch; }
            .search-box { flex: 1; }
            .table-custom thead th,
            .table-custom tbody td { padding: 10px 14px; }
            .main-wrapper { padding: 20px 10px 60px; }
        }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>

<!-- Animated background -->
<div class="bg-layer">
    <div class="bg-orb"></div>
    <div class="bg-orb"></div>
    <div class="bg-orb"></div>
</div>
<div class="bg-grid"></div>

<!-- Toast container -->
<div class="toast-container" id="toast-container"></div>

<!-- Modal container -->
<div id="modal-container"></div>

<div class="main-wrapper">
    <div style="max-width: 920px; margin: 0 auto;">

        <!-- Header -->
        <header class="page-header">
            <div class="badge-label"><i class="fas fa-database"></i> PostgreSQL &middot; Render</div>
            <h1>Student <span>Database</span></h1>
            <p>Manage student records with real-time CRUD operations backed by a persistent PostgreSQL instance.</p>
        </header>

        <!-- Stats -->
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-users"></i></div>
                <div class="stat-number" id="stat-total">0</div>
                <div class="stat-label">Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-layer-group"></i></div>
                <div class="stat-number" id="stat-grades">0</div>
                <div class="stat-label">Grade Levels</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-shapes"></i></div>
                <div class="stat-number" id="stat-sections">0</div>
                <div class="stat-label">Sections</div>
            </div>
        </div>

        <!-- Main Card -->
        <div class="main-card">

            <!-- Form -->
            <div class="form-section">
                <input type="hidden" id="student-id">
                <div style="display: grid; grid-template-columns: 1fr 100px 120px auto; gap: 12px; align-items: end;">
                    <div>
                        <label class="form-label-custom">Full Name</label>
                        <input type="text" id="name" class="form-control-custom" placeholder="e.g. Juan Dela Cruz">
                    </div>
                    <div>
                        <label class="form-label-custom">Grade</label>
                        <input type="number" id="grade" class="form-control-custom" placeholder="11" min="1" max="12">
                    </div>
                    <div>
                        <label class="form-label-custom">Section</label>
                        <input type="text" id="section" class="form-control-custom" placeholder="E.g. Aquila">
                    </div>
                    <button class="btn-add" id="btn-submit" onclick="saveStudent()">
                        <span class="spinner" id="btn-spinner"></span>
                        <i class="fas fa-plus" id="btn-icon"></i>
                        <span id="btn-text">Add Student</span>
                    </button>
                </div>
            </div>

            <!-- Table -->
            <div class="table-section">
                <div class="table-toolbar">
                    <h2>
                        Records
                        <span class="count-badge" id="count-badge">0</span>
                    </h2>
                    <div class="search-box">
                        <i class="fas fa-search"></i>
                        <input type="text" id="search-input" placeholder="Search name, grade, or section..." oninput="filterTable()">
                    </div>
                </div>
                <div class="table-wrap">
                    <table class="table-custom">
                        <thead>
                            <tr>
                                <th style="border-radius: 0;">Student</th>
                                <th>Grade</th>
                                <th>Section</th>
                                <th style="text-align: right; border-radius: 0;">Actions</th>
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
    let allStudents = [];

    /* Avatar color generator based on name */
    const avatarColors = [
        '#10b981','#06b6d4','#f59e0b','#8b5cf6','#ec4899',
        '#ef4444','#14b8a6','#f97316','#6366f1','#84cc16'
    ];
    function getAvatarColor(name) {
        let hash = 0;
        for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
        return avatarColors[Math.abs(hash) % avatarColors.length];
    }
    function getInitials(name) {
        return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    }

    /* Toast notification */
    function showToast(message, type = 'success') {
        const icons = { success: 'fa-check-circle', danger: 'fa-trash-alt', info: 'fa-info-circle' };
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast-msg ${type}`;
        toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('leaving');
            setTimeout(() => toast.remove(), 300);
        }, 2500);
    }

    /* Confirm modal */
    function showConfirm(title, msg, onConfirm) {
        const container = document.getElementById('modal-container');
        container.innerHTML = `
            <div class="modal-overlay" id="modal-overlay">
                <div class="modal-box">
                    <div class="modal-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <h3>${title}</h3>
                    <p>${msg}</p>
                    <div class="modal-btns">
                        <button class="btn-cancel" onclick="closeModal()">Cancel</button>
                        <button class="btn-delete" id="modal-confirm-btn">Delete</button>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('modal-confirm-btn').onclick = () => { closeModal(); onConfirm(); };
        document.getElementById('modal-overlay').onclick = (e) => { if (e.target === e.currentTarget) closeModal(); };
    }
    function closeModal() {
        document.getElementById('modal-container').innerHTML = '';
    }

    /* Update stats */
    function updateStats() {
        document.getElementById('stat-total').textContent = allStudents.length;
        const grades = new Set(allStudents.map(s => s.grade).filter(Boolean));
        const sections = new Set(allStudents.map(s => s.section).filter(Boolean));
        document.getElementById('stat-grades').textContent = grades.size;
        document.getElementById('stat-sections').textContent = sections.size;
        document.getElementById('count-badge').textContent = allStudents.length;
    }

    /* Render table */
    function renderTable(data) {
        const list = document.getElementById('student-list');
        if (!data.length) {
            list.innerHTML = `
                <tr><td colspan="4">
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <p>No students found. Add your first record above.</p>
                    </div>
                </td></tr>
            `;
            return;
        }
        list.innerHTML = data.map(s => {
            const color = getAvatarColor(s.name);
            const initials = getInitials(s.name);
            return `
            <tr class="row-enter" id="row-${s.id}">
                <td>
                    <div class="student-name">
                        <div class="student-avatar" style="background: ${color}20; color: ${color}; border: 1px solid ${color}30;">${initials}</div>
                        ${escapeHtml(s.name)}
                    </div>
                </td>
                <td><span class="grade-badge"><i class="fas fa-graduation-cap" style="font-size:11px;"></i> ${escapeHtml(String(s.grade || '—'))}</span></td>
                <td><span class="section-tag">${escapeHtml(s.section || '—')}</span></td>
                <td>
                    <div class="action-btns" style="justify-content: flex-end;">
                        <button class="btn-icon edit" title="Edit" aria-label="Edit student" onclick='editStudent(${JSON.stringify(s).replace(/'/g, "&#39;")})'><i class="fas fa-pen"></i></button>
                        <button class="btn-icon delete" title="Delete" aria-label="Delete student" onclick="confirmDelete(${s.id}, '${escapeHtml(s.name)}')"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </td>
            </tr>`;
        }).join('');
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /* Filter / search */
    function filterTable() {
        const q = document.getElementById('search-input').value.toLowerCase().trim();
        if (!q) { renderTable(allStudents); return; }
        const filtered = allStudents.filter(s =>
            s.name.toLowerCase().includes(q) ||
            String(s.grade).includes(q) ||
            (s.section && s.section.toLowerCase().includes(q))
        );
        renderTable(filtered);
    }

    /* Load data */
    async function load() {
        try {
            const res = await fetch(API);
            const data = await res.json();
            allStudents = data.students || [];
            updateStats();
            renderTable(allStudents);
        } catch (e) {
            showToast('Failed to load data', 'danger');
        }
    }

    /* Save (add or update) */
    async function saveStudent() {
        const id = document.getElementById('student-id').value;
        const name = document.getElementById('name').value.trim();
        const grade = document.getElementById('grade').value;
        const section = document.getElementById('section').value.trim();

        if (!name) { showToast('Please enter a student name', 'danger'); document.getElementById('name').focus(); return; }

        const btn = document.getElementById('btn-submit');
        const spinner = document.getElementById('btn-spinner');
        const icon = document.getElementById('btn-icon');
        spinner.style.display = 'block';
        icon.style.display = 'none';
        btn.disabled = true;

        const payload = { name, grade, section };
        try {
            const url = id ? `${API}/${id}` : API;
            const method = id ? 'PUT' : 'POST';
            await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            showToast(id ? 'Student updated successfully' : 'Student added successfully', 'success');
            reset();
            await load();
        } catch (e) {
            showToast('Operation failed. Try again.', 'danger');
        } finally {
            spinner.style.display = 'none';
            icon.style.display = '';
            btn.disabled = false;
        }
    }

    /* Edit */
    function editStudent(s) {
        document.getElementById('student-id').value = s.id;
        document.getElementById('name').value = s.name;
        document.getElementById('grade').value = s.grade;
        document.getElementById('section').value = s.section;
        const btn = document.getElementById('btn-submit');
        btn.classList.add('updating');
        document.getElementById('btn-text').textContent = 'Update';
        document.getElementById('btn-icon').className = 'fas fa-save';
        document.getElementById('name').focus();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /* Delete with confirm modal */
    function confirmDelete(id, name) {
        showConfirm(
            'Delete Student',
            `Are you sure you want to remove <strong>${name}</strong> from the database? This action cannot be undone.`,
            async () => {
                /* Animate row out */
                const row = document.getElementById(`row-${id}`);
                if (row) row.classList.add('row-exit');
                setTimeout(async () => {
                    try {
                        await fetch(`${API}/${id}`, { method: 'DELETE' });
                        showToast('Student deleted', 'danger');
                        await load();
                    } catch (e) {
                        showToast('Delete failed', 'danger');
                    }
                }, 280);
            }
        );
    }

    /* Reset form */
    function reset() {
        document.getElementById('student-id').value = '';
        document.getElementById('name').value = '';
        document.getElementById('grade').value = '';
        document.getElementById('section').value = '';
        const btn = document.getElementById('btn-submit');
        btn.classList.remove('updating');
        document.getElementById('btn-text').textContent = 'Add Student';
        document.getElementById('btn-icon').className = 'fas fa-plus';
    }

    /* Enter key to submit */
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && ['name', 'grade', 'section'].includes(document.activeElement?.id)) {
            saveStudent();
        }
        if (e.key === 'Escape') { closeModal(); reset(); }
    });

    load();
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_UI)

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
