# sunod-telemetry

Backend telemetry service for the Sunod game project.

This repository is the backend for:
https://github.com/Hansynily/sunod-game

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Jinja2 (admin HTML pages)

## Features

- Collect quest attempt telemetry from the game client
- Store users, quest attempts, selected skills, and RIASEC profile aggregates
- Provide admin API endpoints for user and performance data
- Provide admin web pages to inspect users and user performance

## Project Structure

```text
app/
  main.py                 # FastAPI app entrypoint
  database.py             # Database connection/session config
  models.py               # SQLAlchemy models
  schemas.py              # Pydantic schemas
  routers/telemetry.py    # Telemetry, admin API, admin UI routes
templates/
  users.html
  user_performance.html
requirements.txt
```

## Prerequisites

- Python 3.10+ (recommended)
- PostgreSQL running locally (default: port 5432)

## Environment Variables

The app reads these variables from environment:

- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (default: `postgres`)
- `POSTGRES_DB` (default: `telemetry_db`)
- `POSTGRES_HOST` (default: `localhost`)
- `POSTGRES_PORT` (default: `5432`)

## Run Locally

### 1. Clone and enter the repo

```bash
git clone https://github.com/Hansynily/sunod-telemetry.git
cd sunod-telemetry
```

### 2. Create and activate virtual environment

Windows (PowerShell):

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows (CMD):

```cmd
py -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database

Create a database named `telemetry_db` (or use your own name and set env vars).

### 5. Set environment variables

PowerShell:

```powershell
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="postgres"
$env:POSTGRES_DB="telemetry_db"
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
```

CMD:

```cmd
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=postgres
set POSTGRES_DB=telemetry_db
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
```

### 6. Start the server

```bash
py -m uvicorn app.main:app --reload
```

On startup, tables are auto-created via SQLAlchemy metadata.

## Local URLs

- API root docs (Swagger): `http://127.0.0.1:8000/docs`
- Admin users page: `http://127.0.0.1:8000/admin/users`

## Main Endpoints

Telemetry:
- `POST /api/telemetry/quest-attempt`
- `POST /api/telemetry/users`
- `GET /api/telemetry/users/{user_id}`
- `POST /api/telemetry/users/{user_id}/quest-attempts`
- `GET /api/telemetry/users/{user_id}/quest-attempts`

Admin API:
- `GET /api/admin/users`
- `GET /api/admin/users/{user_id}`
- `GET /api/admin/users/{user_id}/performance`

Admin UI:
- `GET /admin/users`
- `GET /admin/users/{user_id}`
- `POST /admin/users/{user_id}/delete`
