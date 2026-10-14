import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hostel_waste_devops_secret_key_2026')

# Path to SQLite database inside data/ directory
DATABASE_PATH = 'data/waste_collection.db'
app.config['DATABASE'] = DATABASE_PATH

VALID_WASTE_TYPES = [
    'Household Waste',
    'Plastic Waste',
    'E-Waste',
    'Organic Waste',
    'Construction Waste',
    'Other'
]

VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
VALID_STATUSES = ['Pending', 'Assigned', 'Collected', 'Completed']


def get_db_path():
    """Retrieve current database path from configuration."""
    return app.config.get('DATABASE', DATABASE_PATH)


def get_db_connection():
    """Create a database connection with Row factory enabled."""
    db_file = get_db_path()
    db_dir = os.path.dirname(db_file)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database and create waste_requests table if it doesn't exist."""
    db_file = get_db_path()
    db_dir = os.path.dirname(db_file)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS waste_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waste_type TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


# Initialize database automatically when application starts
with app.app_context():
    init_db()


@app.route('/')
def index():
    """Home page displaying system overview and live metrics."""
    summary = {
        'total': 0,
        'pending': 0,
        'assigned': 0,
        'collected': 0,
        'completed': 0
    }
    recent_requests = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM waste_requests')
            summary['total'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Pending'")
            summary['pending'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Assigned'")
            summary['assigned'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Collected'")
            summary['collected'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Completed'")
            summary['completed'] = cursor.fetchone()[0]

            cursor.execute('SELECT * FROM waste_requests ORDER BY id DESC LIMIT 5')
            recent_requests = cursor.fetchall()
    except Exception as e:
        app.logger.error(f"Error fetching stats: {e}")

    return render_template('index.html', summary=summary, recent_requests=recent_requests)


@app.route('/report', methods=['GET', 'POST'])
def report():
    """Display waste reporting form (GET) or handle submission (POST)."""
    if request.method == 'POST':
        return submit_request()
    return render_template(
        'report.html',
        waste_types=VALID_WASTE_TYPES,
        priorities=VALID_PRIORITIES
    )


@app.route('/submit_request', methods=['POST'])
def submit_request():
    """Handle new waste collection request submission with validation."""
    waste_type = request.form.get('waste_type', '').strip()
    location = request.form.get('location', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority', 'Medium').strip()

    # Form Validations
    errors = []
    if not waste_type or waste_type not in VALID_WASTE_TYPES:
        errors.append("Please select a valid waste type.")
    if not location or len(location) < 3:
        errors.append("Please provide a valid hostel location (at least 3 characters).")
    if not description or len(description) < 5:
        errors.append("Please provide a short description (at least 5 characters).")
    if priority not in VALID_PRIORITIES:
        priority = 'Medium'

    if errors:
        for err in errors:
            flash(err, 'danger')
        return redirect(url_for('report'))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO waste_requests (waste_type, location, description, priority, status)
                VALUES (?, ?, ?, ?, 'Pending')
            ''', (waste_type, location, description, priority))
            conn.commit()
            request_id = cursor.lastrowid

        flash(
            f"Waste collection request submitted successfully! Your Request ID is #{request_id}.",
            'success'
        )
        return redirect(url_for('track', id=request_id))
    except Exception as e:
        flash(f"Database error while saving request: {str(e)}", 'danger')
        return redirect(url_for('report'))


@app.route('/track', methods=['GET', 'POST'])
def track():
    """Track request status by Request ID."""
    req_id = request.args.get('id') or request.form.get('id')
    request_data = None
    not_found = False

    if req_id:
        req_id = str(req_id).strip().replace('#', '')
        if req_id.isdigit():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM waste_requests WHERE id = ?', (int(req_id),))
                request_data = cursor.fetchone()
                if not request_data:
                    not_found = True
        else:
            flash("Invalid Request ID format. Please enter numbers only.", "warning")
            not_found = True

    return render_template(
        'track.html',
        request_data=request_data,
        searched_id=req_id,
        not_found=not_found
    )


@app.route('/admin')
def admin():
    """Admin dashboard displaying summary cards and all collection requests."""
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('q', '').strip()

    summary = {
        'total': 0,
        'pending': 0,
        'assigned': 0,
        'collected': 0,
        'completed': 0
    }

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Summary calculations
        cursor.execute('SELECT COUNT(*) FROM waste_requests')
        summary['total'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Pending'")
        summary['pending'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Assigned'")
        summary['assigned'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Collected'")
        summary['collected'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM waste_requests WHERE status = 'Completed'")
        summary['completed'] = cursor.fetchone()[0]

        # Filtered request retrieval
        base_query = 'SELECT * FROM waste_requests'
        params = []
        conditions = []

        if status_filter and status_filter in VALID_STATUSES:
            conditions.append('status = ?')
            params.append(status_filter)

        if search_query:
            conditions.append('(location LIKE ? OR description LIKE ? OR waste_type LIKE ? OR CAST(id AS TEXT) LIKE ?)')
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])

        if conditions:
            base_query += ' WHERE ' + ' AND '.join(conditions)

        base_query += ' ORDER BY id DESC'
        cursor.execute(base_query, tuple(params))
        requests_list = cursor.fetchall()

    return render_template(
        'admin.html',
        summary=summary,
        requests=requests_list,
        valid_statuses=VALID_STATUSES,
        current_filter=status_filter,
        search_query=search_query
    )


@app.route('/update_status', methods=['POST'])
def update_status():
    """Update status of a waste collection request (Admin action)."""
    req_id = request.form.get('request_id', '').strip()
    new_status = request.form.get('new_status', '').strip()

    if not req_id or not req_id.isdigit():
        flash("Invalid Request ID supplied.", "danger")
        return redirect(url_for('admin'))

    if new_status not in VALID_STATUSES:
        flash("Invalid status transition requested.", "danger")
        return redirect(url_for('admin'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, status FROM waste_requests WHERE id = ?', (int(req_id),))
        existing = cursor.fetchone()

        if not existing:
            flash(f"Request #{req_id} does not exist.", "warning")
            return redirect(url_for('admin'))

        cursor.execute(
            'UPDATE waste_requests SET status = ? WHERE id = ?',
            (new_status, int(req_id))
        )
        conn.commit()

    flash(f"Status for Request #{req_id} successfully updated to '{new_status}'.", "success")
    return redirect(url_for('admin'))


if __name__ == '__main__':
    # Host on 0.0.0.0 and port 5000 as required for Docker and local execution
    app.run(host='0.0.0.0', port=5000, debug=True)
