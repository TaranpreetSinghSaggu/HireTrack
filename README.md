# HireTrack

A full-stack web application designed to manage campus placement activities efficiently.

## 🚀 Tech Stack
- Backend: Flask
- Frontend: Vue.js
- Database: SQLite
- Caching: Redis
- Async Jobs: Celery

## 👥 Roles
- Admin (Institute)
- Company
- Student

## ✨ Features
- Role-based authentication
- Company and drive approvals
- Student applications tracking
- Placement history
- Async job processing (reminders, reports, exports)
- Redis caching for performance

## 📂 Project Structure
- `/frontend` → VueJS UI
- `/backend` → Flask API

## ⚙️ Setup Instructions
(To be added)

## Backend Setup

Run these commands from `D:\PPA\HireTrack`.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy or edit `backend\.env` if needed. The committed template is `backend\.env.example`.
For Redis on WSL:

```powershell
wsl
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping
```

Start the API:

```powershell
cd backend
python app.py
```

Start Celery worker in another activated terminal:

```powershell
cd backend
celery -A celery_worker.celery_app worker --pool=solo --loglevel=info
```

Start Celery Beat in another activated terminal:

```powershell
cd backend
celery -A celery_worker.celery_app beat --loglevel=info
```

Default admin login is:

```text
email: admin@ppa.com
password: admin123
```

If you already have an older SQLite database, back it up before schema-changing tests:

```powershell
Copy-Item backend\placement.db backend\placement.db.bak
```

## Backend Smoke Checks

Use PowerShell `Invoke-RestMethod` or Postman.

1. `POST /api/auth/login` with admin credentials.
2. `POST /api/auth/register/company`, then admin `POST /api/admin/approve-company/<company_id>`.
3. Company login, `POST /api/company/create-job`, then admin `POST /api/admin/approve-job/<job_id>`.
4. Student register/login, `PATCH /api/student/profile`, `GET /api/student/jobs`, `POST /api/student/apply`.
5. Company `GET /api/company/applicants/<job_id>`, status update to `Shortlisted`, then `POST /api/company/applications/<application_id>/schedule-interview`.
6. Student `GET /api/student/applications`, `GET /api/student/interviews`, and after selected/placed, `GET /api/student/placements`.
7. Trigger exports with `POST /api/student/export` or `POST /api/company/export`, then check `GET /api/task/<task_id>`.
