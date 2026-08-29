# Skinora — Automated Testing

## Overview

Two layers of automated testing are provided:

| Layer | Tool | What it tests |
|---|---|---|
| Unit + Integration | **Pytest** | Flask routes, input validation, auth, DB logic |
| API / Manual | **Postman** | Full API flow against the live running server |

---

## Pytest (Backend Unit Tests)

### What is tested

| File | Endpoint(s) | Tests |
|---|---|---|
| `test_health.py` | `GET /api/health` | Server up, DB connected |
| `test_auth.py` | `/api/auth/*` | Login success/failure, register validation, OTP, token auth |
| `test_remedies.py` | `/api/remedies` | Auth guard, missing param, results, 404 |
| `test_tracking.py` | `/api/tracking/*` | Create, toggle reminders, checkin, dashboard, due |
| `test_questionnaire.py` | `/api/questionnaire/*` | Submit answers, validation, lifestyle |

Total: **30 test cases**

### Setup

From the `backend/` directory:

```bash
# 1. Activate virtual environment
.\venv\Scripts\activate          # Windows PowerShell
# or: source venv/bin/activate   # Mac / Linux

# 2. Install pytest (only needed once)
pip install pytest

# 3. Run all tests
pytest tests/ -v

# 4. Run a single test file
pytest tests/test_auth.py -v

# 5. Run with a short summary report
pytest tests/ -v --tb=short
```

**No MySQL required** — tests use an SQLite file (`tests/test_skinora.db`) that is
created automatically before the session and deleted when it ends.
Your production database is never touched.

### Expected output

```
tests/test_health.py::test_health_returns_200          PASSED
tests/test_health.py::test_health_db_connected         PASSED
tests/test_auth.py::TestLogin::test_missing_...        PASSED
...
30 passed in X.Xs
```

---

## Postman (API Testing)

### Setup

1. Open Postman → **Import** → select `tests/postman/Skinora_API.postman_collection.json`
2. Make sure the Flask backend is running: `python run.py`
3. In the collection, set the **base_url** variable to `http://localhost:5000`

### Recommended run order

1. **Health Check** — confirm server is up
2. **Auth → send-otp** → **verify-otp** → **register** → **login** (token auto-saved)
3. **Remedies** — list, get by ID
4. **Questionnaire** — submit, lifestyle
5. **Tracking** — create, toggle reminders, checkin, dashboard

The **login** request automatically saves the JWT to the `token` collection variable,
so all subsequent requests in the collection are pre-authenticated.

### Running the full collection automatically

In Postman: **Collections → Run collection** → click **Run Skinora API**.
All 20 Postman test scripts run in order and a pass/fail report is shown.

---

## What Each Test Verifies (for FYP document)

| Test category | Verification |
|---|---|
| Health check | Backend server responds and database connection is live |
| Login validation | Missing fields, unknown user, wrong password each return correct HTTP codes |
| Login success | Valid credentials return a JWT token and user profile |
| Registration | OTP verification required; duplicate email rejected |
| Auth guard | Every protected endpoint returns 401 without a valid token |
| Remedies list | Returns remedies for a given skin condition; empty list for unknown condition |
| Remedies 404 | Non-existent remedy ID returns 404 |
| Questionnaire | Empty answers rejected (400); valid answers return lifestyle summary + validation score |
| Tracking create | Missing remedy_id / invalid frequency rejected; valid request creates plan |
| Toggle reminders | Pause/resume toggles `reminders_paused` correctly |
| Checkin | Invalid status rejected; dashboard and due-check return correct structure |
