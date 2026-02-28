# sunod-telemetry

Backend telemetry service for **Sunod** (add hyperlink once game repo has been uploaded plox thx). This backend tracks player sessions, quest attempts, skill usage, and RIASEC profile progression.

Built with **FastAPI** + **PostgreSQL**.

Might change the tech stack from paper's architectural diagram. PostgreSQL > MongoDB

---

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Pydantic
- Uvicorn

---

## Build

### 1. Clone the repo

```bash
git clone https://github.com/Hansynily/sunod-telemetry.git
cd sunod-telemetry
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a database and update connection string in `app/database.py`:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/sunod"
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`.

---

## API Overview

### Telemetry endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/telemetry/users` | Create a new user |
| GET | `/api/telemetry/users/{user_id}` | Get a user by ID |
| POST | `/api/telemetry/users/{user_id}/quest-attempts` | Submit a quest attempt |
| GET | `/api/telemetry/users/{user_id}/quest-attempts` | List quest attempts for a user |
| POST | `/api/telemetry/quest-attempt` | Submit full quest attempt telemetry (primary Unity endpoint) |

### Admin API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | List all players |
| GET | `/api/admin/users/{user_id}` | Get a player by ID |
| GET | `/api/admin/users/{user_id}/performance` | Get full performance + RIASEC data |

### Admin UI

| Route | Description |
|-------|-------------|
| `/admin/users` | Players list page |
| `/admin/users/{user_id}` | Player performance page |

Interactive API docs available at `http://localhost:8000/docs`.

---

## Primary Unity Endpoint

The main endpoint used by the Unity game client is:

```
POST /api/telemetry/quest-attempt
```

It creates the player if new, logs the quest attempt, records skills used, and updates the RIASEC profile.

**Expected payload:**

```json
{
  "player_id": "unique-device-or-generated-id",
  "username": "player_name",
  "quest_id": "floor_01",
  "quest_result": "success",
  "time_spent_seconds": 120,
  "selected_skills": [
    { "skill_name": "Logical Reasoning", "riasec_code": "I" },
    { "skill_name": "Creative Design", "riasec_code": "A" }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Quest attempt telemetry recorded successfully."
}
```

---

## RIASEC Framework

Skills used during runs are tagged with a RIASEC code (`R`, `I`, `A`, `S`, `E`, `C`). The backend automatically accumulates these into a per-player RIASEC profile, which can be queried via the admin performance endpoint.

---

## Project Structure

```
sunod-telemetry/
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # DB connection and session
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   └── routers/
│       └── telemetry.py # All route handlers
├── templates/
│   ├── users.html             # Admin players list
│   └── user_performance.html  # Admin player performance
└── requirements.txt
```

---

## To-Do

- [ ] Temporarily remove `email` field requirement from user creation (mmm not really needed during demo/survey phase)
---

## Related

- Unity game client repo: *(TBA TBA TBA TBA)*
