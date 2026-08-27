# Rural Enterprise Advisory API

## 1. Project Overview

A small, fictional Flask REST API representing the backend of a platform
that helps coordinators manage rural micro-enterprises through this
workflow:

```
Beneficiary -> Digital Enterprise Profile -> Feasibility Analysis
            -> Financial Planning -> Scheme Matching -> Monitoring
```

## 2. Purpose of This POC

This project is a **DevSecOps / Secure SDLC proof of concept**, built by a
cybersecurity intern. Its purpose is to provide a realistic-but-small
Flask API that can later be scanned and tested with a security pipeline:

- Ruff (linting)
- TruffleHog (secret scanning)
- GitHub CodeQL (SAST)
- pip-audit (dependency scanning)
- pytest (automated tests)
- OWASP ZAP (DAST)

**No GitHub Actions / CI pipeline is included yet.** The application is
meant to be verified on its own first; the security pipeline will be
added in a later phase.

All data, credentials, and "AI" logic in this project are fictional and
for demonstration only.

## 3. Technology Stack

- Python 3.12
- Flask (REST API)
- PyMongo (MongoDB driver) — with an in-memory fallback for local dev/tests
- PyJWT (simple token-based auth)
- python-dotenv (loads `.env` for local configuration)
- pytest (automated tests)

No frontend framework, no real AI/ML service, no Docker, and no cloud
deployment are part of this POC.

## 4. Project Structure

```
rural-enterprise-advisor/
├── app/
│   ├── __init__.py       # App factory, blueprint registration
│   ├── config.py         # Configuration from environment variables
│   ├── extensions.py     # Database abstraction (MongoDB / in-memory)
│   ├── auth.py           # Login endpoint + require_auth decorator
│   ├── enterprises.py    # Enterprise profile CRUD
│   ├── finance.py        # Financial assessment calculations
│   ├── feasibility.py    # Mock feasibility analysis
│   ├── schemes.py        # Fictional scheme listing/matching
│   └── dashboard.py      # Aggregated dashboard summary
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_auth.py
│   ├── test_enterprises.py
│   └── test_finance.py
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```

## 5. Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the example environment file and adjust as needed:

```bash
cp .env.example .env
```

## 6. Environment Variables

| Variable            | Purpose                                              | Example                                              |
|---------------------|-------------------------------------------------------|-------------------------------------------------------|
| `JWT_SECRET`        | Secret used to sign login tokens (local dev only)     | `replace-with-local-development-secret`               |
| `JWT_EXPIRY_MINUTES`| How long a login token stays valid                    | `60`                                                   |
| `MONGODB_URI`       | Local MongoDB connection string                       | `mongodb://localhost:27017/rural_enterprise_advisor`  |
| `USE_IN_MEMORY_DB`  | `true` to skip MongoDB and use an in-memory store      | `false`                                                |
| `DEMO_USERNAME`     | Demo login username (not a real secret)               | `coordinator`                                          |
| `DEMO_PASSWORD`     | Demo login password (not a real secret)               | `demo-password-123`                                    |

`.env` is git-ignored. Only `.env.example` (with placeholder values) is
committed.

## 7. MongoDB Setup

If you have MongoDB installed locally, start it with:

```bash
mongod --dbpath /path/to/your/data/directory
```

If you don't want to run MongoDB locally, set `USE_IN_MEMORY_DB=true` in
your `.env` file. The app will then use a simple in-memory data store
instead (data is lost when the app stops — this is only meant for quick
local testing, not persistence). The automated test suite always uses
this in-memory store automatically, so tests never require MongoDB.

## 8. Running the Application

```bash
python run.py
```

The API will be available at:

```
http://127.0.0.1:5000
```

## 9. Running Tests

```bash
pytest
```

Tests use Flask's test client and the in-memory database backend, so
they run without any external services.

## 10. Running Ruff

Ruff is not configured yet (a later phase will add CI linting), but you
can run it manually against the current code:

```bash
ruff check .
```

## 11. API Endpoint List

| Method | Path                                              | Auth required |
|--------|----------------------------------------------------|----------------|
| GET    | `/health`                                           | No             |
| POST   | `/api/auth/login`                                   | No             |
| POST   | `/api/enterprises`                                  | Yes            |
| GET    | `/api/enterprises`                                  | Yes            |
| GET    | `/api/enterprises/<id>`                             | Yes            |
| PUT    | `/api/enterprises/<id>`                             | Yes            |
| DELETE | `/api/enterprises/<id>`                             | Yes            |
| POST   | `/api/enterprises/<id>/financial-assessment`        | Yes            |
| POST   | `/api/enterprises/<id>/feasibility`                 | Yes            |
| GET    | `/api/schemes`                                      | Yes            |
| POST   | `/api/enterprises/<id>/scheme-match`                | Yes            |
| GET    | `/api/dashboard/summary`                            | Yes            |

Authenticated requests must include:

```
Authorization: Bearer <token>
```

## 12. Example Requests/Responses

**Login**

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "coordinator", "password": "demo-password-123"}'
```

```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

**Create an enterprise**

```bash
curl -X POST http://127.0.0.1:5000/api/enterprises \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt>" \
  -d '{
    "business_name": "Sunrise Dairy Co-op",
    "business_type": "Dairy processing",
    "location": "Sample District",
    "target_customers": "Local households",
    "margin_capital": 20000,
    "expected_investment": 100000,
    "available_assets": 15000,
    "workforce": 4,
    "revenue": 5000,
    "expenses": 3000,
    "existing_loans": 0
  }'
```

**Feasibility analysis**

```bash
curl -X POST http://127.0.0.1:5000/api/enterprises/<id>/feasibility \
  -H "Authorization: Bearer <jwt>"
```

```json
{
  "viability_score": 78,
  "market_reach": "moderate",
  "competition": "low",
  "recommendation": "Proceed with additional working-capital planning",
  "disclaimer": "MOCK/DEMO output generated by deterministic logic - not a real AI assessment."
}
```

## 13. Security Considerations

- No real secrets exist anywhere in this repository. `JWT_SECRET`, the
  demo login credentials, and `MONGODB_URI` are all read from
  environment variables with only placeholder values in `.env.example`.
- The demo login (`DEMO_USERNAME` / `DEMO_PASSWORD`) is intentionally
  simple and is **not** a production authentication mechanism.
- All database lookups use PyMongo query objects (e.g. `{"id": doc_id}`)
  — no string concatenation is used to build queries.
- `eval()` and `exec()` are not used anywhere in this codebase.
- API responses never include passwords, tokens, or stack traces.
- Generic error handlers return plain JSON error messages instead of
  leaking internal details.
- This is a small educational POC — it does not implement every
  production-grade security control (e.g. rate limiting, password
  hashing/user management, refresh tokens, audit logging).

## 14. Important Disclaimers

- **All enterprise, financial, and scheme data in this project is
  fictional.** No real people, businesses, or government programs are
  represented.
- **This is not a production financial application** and does not
  provide real financial or scheme-eligibility advice. It exists solely
  as a DevSecOps / security-testing proof of concept.
