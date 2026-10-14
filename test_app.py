import os
import sqlite3
import pytest
from app import app, init_db, get_db_connection


@pytest.fixture
def client(tmp_path):
    """Fixture to configure Flask test client with an isolated temporary SQLite database."""
    # Create isolated database file inside pytest tmp_path
    test_db_dir = tmp_path / "data"
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db_path = str(test_db_dir / "waste_collection.db")

    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = test_db_path
    app.config['WTF_CSRF_ENABLED'] = False

    # Initialize schema in the temporary test database
    with app.app_context():
        init_db()

    with app.test_client() as test_client:
        yield test_client


def test_app_starts():
    """Verify that the Flask application initializes properly."""
    assert app is not None
    assert app.name == 'app'


def test_home_page_returns_200(client):
    """Verify that the home page (/) returns HTTP 200 OK and contains key titles."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hostel Waste Management" in response.data or b"HMS EcoClean" in response.data
    assert b"Report Waste Collection" in response.data


def test_report_page_returns_200(client):
    """Verify that the waste reporting form (/report) returns HTTP 200 OK."""
    response = client.get('/report')
    assert response.status_code == 200
    assert b"Report Waste for Collection" in response.data
    assert b"waste_type" in response.data
    assert b"location" in response.data


def test_submit_waste_request_and_stored_in_sqlite(client):
    """Verify that a resident can submit a waste collection request and it is saved to SQLite."""
    payload = {
        'waste_type': 'Plastic Waste',
        'location': 'Hostel Block-B, Room 204',
        'description': 'Three cartons full of used plastic bottles and packaging.',
        'priority': 'High'
    }

    # Submit form via POST
    response = client.post('/submit_request', data=payload, follow_redirects=False)
    
    # Must redirect to tracking page
    assert response.status_code == 302
    assert '/track?id=1' in response.headers['Location']

    # Directly inspect the SQLite database to confirm record was stored
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM waste_requests WHERE id = 1")
            row = cursor.fetchone()

            assert row is not None
            assert row['id'] == 1
            assert row['waste_type'] == 'Plastic Waste'
            assert row['location'] == 'Hostel Block-B, Room 204'
            assert row['description'] == 'Three cartons full of used plastic bottles and packaging.'
            assert row['priority'] == 'High'
            assert row['status'] == 'Pending'


def test_submit_invalid_request_fails_gracefully(client):
    """Verify that invalid inputs are rejected and not stored in the database."""
    invalid_payload = {
        'waste_type': 'InvalidTypeNotAllowed',
        'location': 'A',  # Too short
        'description': 'Bad',  # Too short
        'priority': 'Medium'
    }

    response = client.post('/submit_request', data=invalid_payload, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please select a valid waste type" in response.data or b"valid hostel location" in response.data

    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM waste_requests")
            assert cursor.fetchone()[0] == 0


def test_track_page_with_valid_and_invalid_id(client):
    """Verify that tracking retrieves active ticket and handles nonexistent IDs."""
    # 1. Insert a request
    payload = {
        'waste_type': 'Organic Waste',
        'location': 'Mess Dining Hall Backdoor',
        'description': 'Leftover food scraps from lunch mess.',
        'priority': 'Urgent'
    }
    client.post('/submit_request', data=payload)

    # 2. Track existing request #1
    response = client.get('/track?id=1')
    assert response.status_code == 200
    assert b"Request #1" in response.data
    assert b"Organic Waste" in response.data
    assert b"Mess Dining Hall Backdoor" in response.data
    assert b"Pending" in response.data

    # 3. Track non-existent request #9999
    response_missing = client.get('/track?id=9999')
    assert response_missing.status_code == 200
    assert b"Request Not Found" in response_missing.data


def test_admin_dashboard_returns_200(client):
    """Verify that admin dashboard (/admin) returns HTTP 200 and displays metrics and records."""
    # Insert two test records
    client.post('/submit_request', data={
        'waste_type': 'E-Waste',
        'location': 'Computer Lab Block C',
        'description': 'Defective CRT monitor and mouse cables.',
        'priority': 'Low'
    })

    response = client.get('/admin')
    assert response.status_code == 200
    assert b"Waste Collection Oversight" in response.data
    assert b"Total Requests" in response.data
    assert b"Computer Lab Block C" in response.data
    assert b"E-Waste" in response.data


def test_admin_status_update_lifecycle(client):
    """Verify admin can advance request status: Pending -> Assigned -> Collected -> Completed."""
    # 1. Create a request
    client.post('/submit_request', data={
        'waste_type': 'Household Waste',
        'location': 'Wing 3 Common Balcony',
        'description': 'Cardboard packing boxes and paper.',
        'priority': 'Medium'
    })

    # Lifecycle step 1: Pending -> Assigned
    resp1 = client.post('/update_status', data={'request_id': '1', 'new_status': 'Assigned'})
    assert resp1.status_code == 302
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM waste_requests WHERE id = 1")
            assert cursor.fetchone()[0] == 'Assigned'

    # Lifecycle step 2: Assigned -> Collected
    resp2 = client.post('/update_status', data={'request_id': '1', 'new_status': 'Collected'})
    assert resp2.status_code == 302
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM waste_requests WHERE id = 1")
            assert cursor.fetchone()[0] == 'Collected'

    # Lifecycle step 3: Collected -> Completed
    resp3 = client.post('/update_status', data={'request_id': '1', 'new_status': 'Completed'})
    assert resp3.status_code == 302
    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM waste_requests WHERE id = 1")
            assert cursor.fetchone()[0] == 'Completed'


def test_admin_rejects_invalid_status(client):
    """Verify that invalid status transitions are rejected."""
    client.post('/submit_request', data={
        'waste_type': 'Other',
        'location': 'Hostel Yard',
        'description': 'Miscellaneous garden clippings.',
        'priority': 'Low'
    })

    response = client.post('/update_status', data={'request_id': '1', 'new_status': 'NonExistentStatus'})
    assert response.status_code == 302

    with app.app_context():
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM waste_requests WHERE id = 1")
            assert cursor.fetchone()[0] == 'Pending'
