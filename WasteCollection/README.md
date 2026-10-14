# Hostel Management System - Waste Collection & Tracking System

[![Flask](https://img.shields.io/badge/Framework-Flask%203.0+-green.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%203-lightgrey.svg)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg)](https://www.docker.com/)
[![Testing](https://img.shields.io/badge/Testing-Pytest-yellow.svg)](https://pytest.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939.svg)](https://www.jenkins.io/)
[![Automation](https://img.shields.io/badge/Deployment-Ansible-EE0000.svg)](https://www.ansible.com/)

A simple, robust, and professional college-level DevOps project demonstrating a functional web application integrated with an end-to-end Automated CI/CD and Container Deployment pipeline.

---

## 1. Project Overview

The **Hostel Waste Collection & Tracking System** solves the daily operational challenge of waste segregation, collection, and disposal in college hostels. It provides a simple, clean, and responsive web interface for:
1. **Hostel Residents (Students)**: Report accumulated waste (e.g., room garbage, dining hall leftovers, packaging cartons, or e-waste), choose urgency, receive an immediate Request ID, and track live status.
2. **Hostel Administration (Wardens/Sanitation Staff)**: Monitor requests on a centralized dashboard, review details, and transition requests through their lifecycle (`Pending` &rarr; `Assigned` &rarr; `Collected` &rarr; `Completed`).

Behind this functional web application lies an **industry-standard DevOps infrastructure**:
- **Pytest** ensures zero regressions before deployment.
- **Docker** packages the Python Flask runtime into an isolated, portable container.
- **Jenkins** automates building and testing upon every git commit.
- **Ansible** deploys and runs the container with desired state configuration.
- **Docker Volume** (`waste_collection_data`) guarantees that SQLite records survive container recreations and restarts.

---

## 2. Technology Stack

### Frontend:
- **HTML5**: Semantic, accessible markup.
- **CSS3**: Custom modern responsive styling (Plus Jakarta Sans, CSS variables, flexbox & grid, color-coded badges, visual stepper).
- **JavaScript (Vanilla)**: Dynamic form validation, auto-dismissing alerts, and client-side table search filtering.

### Backend:
- **Python 3.11**: Clean, lightweight runtime.
- **Flask**: Python microframework providing routing, flash messaging, and Jinja2 templating.

### Database:
- **SQLite 3**: Embedded relational database stored strictly at `data/waste_collection.db` with parameterized queries to prevent SQL injection.

### DevOps & Infrastructure:
- **Git & GitHub**: Distributed version control and remote repository management.
- **Docker**: Containerization using `python:3.11-slim` with port mapping `5002:5000`.
- **Docker Volume**: `waste_collection_data` mounted to `/app/data` for permanent data persistence.
- **Pytest**: Automated test suite for unit and integration testing inside Docker.
- **Jenkins**: Declarative CI/CD pipeline automating **Build ➔ Test ➔ Deploy**.
- **Ansible**: Configuration management and container orchestration via the `community.docker.docker_container` module.

---

## 3. Architecture & Workflows

### 3.1 Important Architectural Separation

> [!IMPORTANT]
> The **Application Flow** is strictly decoupled from the **DevOps CI/CD Flow**.
> - Submitting or updating a waste request modifies the **SQLite database** directly inside the running container; it **does NOT** trigger Jenkins.
> - Jenkins is **only** triggered when a developer pushes source code updates to Git/GitHub.
> - Ansible ensures the Docker container is running with the specified volume and ports.

---

### 3.2 Application Flow (User Interaction)

```
Resident / Student
       │
       ▼
Open Website (/)
       │
       ▼
Report Waste (/report)
       │
       ├── Select Waste Type (Household, Plastic, E-Waste, Organic, Construction, Other)
       ├── Enter Location (e.g. Block B, Room 204)
       ├── Enter Short Description
       └── Choose Priority (Low, Medium, High, Urgent)
       │
       ▼
Submit Form (POST /submit_request)
       │
       ▼
Flask Backend (app.py)
       │
       ▼
SQLite Database (data/waste_collection.db)
       │
       ▼
Request ID Generated (e.g. #1) ──► Resident Tracks Status (/track?id=1)
                                            │
                                            ▼
Admin Dashboard (/admin) ◄────── Status: Pending 
       │
       ▼
Admin Updates Status (POST /update_status)
       │
       ▼
Pending ──► Assigned ──► Collected ──► Completed
       │
       ▼
SQLite Database Updated ──► Live Status Displayed to Resident
```

---

### 3.3 DevOps CI/CD Flow (Developer & Infrastructure)

```
Developer
    │
    ▼ (git commit & git push)
Git / GitHub
    │
    ▼ (Webhook / SCM Polling)
Jenkins CI/CD
    │
    ├── Stage 1: Checkout Latest Source Code
    │
    ├── Stage 2: Build Docker Image
    │            docker build -t waste-collection-ci .
    │
    ├── Stage 3: Run Automated Pytest
    │            docker run --rm waste-collection-ci python -m pytest test_app.py
    │
    └── Stage 4: Deploy with Ansible
                 docker exec ansible-docker-lab \
                 ansible-playbook -i /inventory.ini /waste-deploy.yml
                 │
                 ▼
          Ansible Container Orchestrator
                 │
                 ▼ (ensures volume & container state)
          Docker Engine
                 │
                 ├── Docker Container (waste-collection-ansible)
                 │     └── Python Flask (0.0.0.0:5000 -> Host 5002)
                 │
                 └── Docker Volume (waste_collection_data)
                       └── Mounted at /app/data
                             └── waste_collection.db (Persistent Storage)
```

---

## 4. Project Directory Structure

```
WasteCollection/
│
├── app.py                     # Main Flask application & SQLite routes
├── requirements.txt           # Python project dependencies (Flask, Pytest)
├── Dockerfile                 # Docker configuration for python:3.11-slim
├── Jenkinsfile                # Jenkins 3-stage Declarative CI/CD pipeline
├── waste-deploy.yml           # Ansible playbook deploying the container
├── test_app.py                # Automated Pytest suite (9 tests)
├── .gitignore                 # Git ignore patterns (database, caches, env)
├── README.md                  # Comprehensive project documentation
│
├── templates/                 # Jinja2 HTML5 Templates
│   ├── base.html              # Base master layout with navbar and footer
│   ├── index.html             # Home page with hero, live metrics & guide
│   ├── report.html            # Resident waste reporting form
│   ├── track.html             # Real-time request tracking & stepper UI
│   └── admin.html             # Admin management dashboard & status controls
│
├── static/                    # Frontend Static Assets
│   ├── style.css              # Modern CSS3 stylesheet (eco-theme, responsive)
│   └── script.js              # Client-side validation, search filter & alerts
│
└── data/                      # Persistent database directory
    └── .gitkeep               # Directory placeholder (DB file is gitignored)
```

---

## 5. Database Schema

The database file is stored at:
```
data/waste_collection.db
```

Table: `waste_requests`
```sql
CREATE TABLE IF NOT EXISTS waste_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waste_type TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Supported Values:
- **Waste Types:** `Household Waste`, `Plastic Waste`, `E-Waste`, `Organic Waste`, `Construction Waste`, `Other`
- **Priorities:** `Low`, `Medium`, `High`, `Urgent`
- **Lifecycle Statuses:** `Pending` &rarr; `Assigned` &rarr; `Collected` &rarr; `Completed`

---

## 6. How to Run Locally (Without Docker)

### Prerequisites:
- Python 3.11 or higher installed on your machine.

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "hostel management"
```

### Step 2: Create and Activate a Virtual Environment (Optional but recommended)
**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask Application
```bash
python app.py
```

The application will start on:
```
http://127.0.0.1:5000
```
Open your browser and navigate to `http://localhost:5000`.

---

## 7. How to Run Automated Tests (Pytest)

The test suite tests the application in isolation using temporary test fixtures without touching any production database.

Run:
```bash
python -m pytest test_app.py -v
```

### Tests Covered:
1. `test_app_starts`: Confirms Flask application initializes successfully.
2. `test_home_page_returns_200`: Confirms `/` loads with HTTP 200 and key elements.
3. `test_report_page_returns_200`: Confirms `/report` renders form inputs.
4. `test_submit_waste_request_and_stored_in_sqlite`: Submits valid request, checks 302 redirect to `/track?id=1`, and directly verifies database row in SQLite.
5. `test_submit_invalid_request_fails_gracefully`: Tests input validation rejection.
6. `test_track_page_with_valid_and_invalid_id`: Verifies valid lookup and 404 handling.
7. `test_admin_dashboard_returns_200`: Verifies admin view and summary calculations.
8. `test_admin_status_update_lifecycle`: Validates complete lifecycle (`Pending` ➔ `Assigned` ➔ `Collected` ➔ `Completed`).
9. `test_admin_rejects_invalid_status`: Verifies unauthorized status values are rejected.

---

## 8. Docker Instructions

### 8.1 Build the Docker Image
The Docker image is named `waste-collection-ci`:
```bash
docker build -t waste-collection-ci .
```

### 8.2 Run Automated Tests Inside Docker
```bash
docker run --rm waste-collection-ci python -m pytest test_app.py
```

### 8.3 Run the Application Container with Docker Volume Persistence
Run the container named `waste-collection-ansible` with the volume `waste_collection_data` mounted to `/app/data`:
```bash
docker run -d \
  --name waste-collection-ansible \
  -p 5002:5000 \
  -v waste_collection_data:/app/data \
  --restart unless-stopped \
  waste-collection-ci
```

Access the running container in your browser at:
```
http://localhost:5002
```

---

## 9. How Docker Volume Provides Persistence

In a containerized environment, containers are **ephemeral** by default. If a container is removed (`docker rm`), any files written inside the container's writable layer are destroyed.

To prevent database loss:
1. The SQLite database is created in the `/app/data` directory inside the container (`/app/data/waste_collection.db`).
2. When launching the container, the named volume `waste_collection_data` is mounted to `/app/data`:
   ```bash
   -v waste_collection_data:/app/data
   ```
3. Docker stores the contents of `waste_collection_data` on the host machine storage outside the container lifecycle.
4. **Demonstrating Persistence in Viva/Lab:**
   ```bash
   # 1. Add some waste requests on http://localhost:5002
   # 2. Stop and remove the container:
   docker stop waste-collection-ansible
   docker rm waste-collection-ansible

   # 3. Recreate the container with the same volume:
   docker run -d --name waste-collection-ansible -p 5002:5000 -v waste_collection_data:/app/data waste-collection-ci

   # 4. Refresh http://localhost:5002 -> All previously submitted requests are still intact!
   ```

---

## 10. Jenkins CI/CD Pipeline Explanation

The `Jenkinsfile` defines a Declarative Pipeline running 3 sequential stages:

```groovy
pipeline {
    agent any

    stages {
        // Stage 1: Packages application into an immutable Docker image
        stage('Build') {
            steps {
                sh 'docker build -t waste-collection-ci .'
            }
        }

        // Stage 2: Executes automated test suite inside container sandbox
        stage('Test') {
            steps {
                sh 'docker run --rm waste-collection-ci python -m pytest test_app.py'
            }
        }

        // Stage 3: Triggers Ansible deployment inside the lab control node
        stage('Deploy with Ansible') {
            steps {
                sh '''
                docker exec ansible-docker-lab \
                ansible-playbook \
                -i /inventory.ini \
                /waste-deploy.yml
                '''
            }
        }
    }

    // Post-execution reporting
    post {
        success {
            echo 'SUCCESS: Waste Collection CI/CD Pipeline Completed Successfully!'
        }
        failure {
            echo 'FAILURE: Waste Collection CI/CD Pipeline Failed!'
        }
    }
}
```

### Why this pipeline is reliable:
- If any test fails in **Stage 2**, the pipeline aborts immediately and does **not** proceed to deployment.
- The deployment stage is completely automated, eliminating human error during release.

---

## 11. Ansible Deployment Explanation

The playbook `waste-deploy.yml` uses Ansible's declarative state model:

```yaml
---
- name: Deploy Hostel Waste Collection Tracking System Container
  hosts: all
  become: true
  tasks:
    - name: Ensure persistent Docker volume exists for SQLite database
      community.docker.docker_volume:
        name: waste_collection_data
        state: present

    - name: Deploy or update Waste Collection application container
      community.docker.docker_container:
        name: waste-collection-ansible
        image: waste-collection-ci
        state: "{{ container_state | default('started') }}"
        restart_policy: unless-stopped
        ports:
          - "5002:5000"
        volumes:
          - waste_collection_data:/app/data
```

### Ansible Highlights:
- **Idempotency**: If the container is already running with the correct image, port, and volume, Ansible makes no changes (`ok`). If the image has updated or the container stopped, Ansible recreates/starts it (`changed`).
- **Volume Guarantee**: It ensures `waste_collection_data` is created prior to container spin-up.
- **Port Mapping**: Exposes internal container port `5000` to host port `5002`.

---

## 12. College DevOps Viva / Demonstration Checklist

When presenting this project to an examiner or instructor, highlight the following:

1. **Clean Separation of Concerns**: Explain how the resident flow creates a request in SQLite, while the DevOps pipeline is responsible only for code integration and deployment.
2. **Database Path & Parameterized Queries**: Point to `data/waste_collection.db` in `app.py` and demonstrate parameterized SQL queries preventing injection attacks.
3. **Automated Testing**: Run `python -m pytest test_app.py -v` in the terminal to demonstrate automated tests passing in seconds.
4. **Volume Persistence Demo**: Explain how the Docker volume `waste_collection_data` decouples state from the container lifecycle.
5. **Zero-Downtime Re-deployment**: Show how Ansible updates or redeploys the container cleanly with a single command.

---

## 13. License

Developed for academic and educational demonstration purposes in College DevOps Laboratories. Free to use, adapt, and extend.
