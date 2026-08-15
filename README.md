# LangChain_01

A beginner-friendly, full-stack Retrieval-Augmented Generation application built incrementally with Python.

Each functionality is created, tested, validated and deployed locally before development proceeds to the next functionality.

## Current status

Completed:

- Functionality 0 - Project Foundation
- Functionality 1 - Health and System Status
- Functionality 2 - SQLite Foundation

The application currently provides:

- Python 3.11 virtual environment
- FastAPI backend
- Streamlit frontend
- Dynamic environment configuration
- FastAPI root endpoint
- FastAPI health endpoint
- Streamlit system-status display
- Safe unavailable-backend handling
- SQLite database foundation
- Department, user, role and permission tables
- Controlled ingestion-record structure
- Concurrency-friendly SQLite configuration
- Isolated automated database tests
- Secure Git exclusions

The following features will be added separately:

- Secure authentication
- Admin role assignment
- Role-based authorization
- Policy Maker approval workflow
- Multi-format document ingestion
- Text splitting
- Hugging Face embeddings
- FAISS vector storage and retrieval
- Customer query processing
- Approved website fallback
- Private repeated-issue matching
- LangChain RAG pipeline
- OpenAI answer generation
- LangSmith tracing

## Project structure

```text
LangChain_01/
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── ingestion_models.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── data/
│   └── uploads/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_frontend.py
│   └── test_main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── rag_app.db
└── README.md
```

The `.env`, `venv/` and `rag_app.db` files exist locally but are intentionally excluded from Git.

The SQLite database is generated locally when FastAPI starts. FAISS files will be generated only when the FAISS functionality is implemented.

## Requirements

- Windows 11
- Python 3.11
- Git
- Visual Studio Code

## Create the virtual environment

```bat
py -3.11 -m venv venv
```

Activate it:

```bat
venv\Scripts\activate
```

Verify:

```bat
python --version
```

## Install packages

```bat
python -m pip install -r requirements.txt
```

Verify dependency compatibility:

```bat
python -m pip check
```

## Configure the application

Copy the variable names from `.env.example` into a local `.env` file.

Example development configuration:

```env
APP_NAME=LangChain RAG Application
APP_ENV=development
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
DATABASE_URL=sqlite:///./rag_app.db
```

Supported `APP_ENV` values:

- `development`
- `testing`
- `production`

Configuration values are loaded dynamically. They are not hard-coded in Python.

Never commit `.env` or place API keys in source code.

## Run automated tests

```bat
python -m pytest -v
```

Current expected result:

```text
10 passed
```

Tests do not run automatically when FastAPI or Streamlit starts. Run them manually during development. A CI/CD workflow can automate them later.

## Run the FastAPI backend

Open Terminal 1:

```bat
venv\Scripts\activate
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Health endpoint

Open:

```text
http://127.0.0.1:8000/health
```

Current response:

```json
{
  "status": "healthy",
  "application": "LangChain RAG Application",
  "environment": "development",
  "backend": "available",
  "database": "available",
  "faiss": "not_configured",
  "langsmith": "not_configured"
}
```

The endpoint deliberately excludes:

- API keys
- Database connection strings
- Local filesystem paths
- Authorization headers
- Detailed internal exceptions
- Table contents

FAISS and LangSmith will receive real health checks when their functionalities are implemented.

## Run the Streamlit frontend

Keep FastAPI running in Terminal 1.

Open Terminal 2:

```bat
venv\Scripts\activate
python -m streamlit run frontend\app.py --server.address 127.0.0.1 --server.port 8501
```

Frontend:

```text
http://127.0.0.1:8501
```

The frontend calls FastAPI's `/health` endpoint and displays:

- Backend availability
- Database status
- FAISS status
- LangSmith status
- Current environment

If FastAPI is stopped, Streamlit displays a safe unavailable-backend message instead of crashing.

Stop either local server using:

```text
Ctrl+C
```

## SQLite database foundation

The application uses SQLite during local development:

```text
rag_app.db
```

The database is initialized when FastAPI starts. Existing tables and rows are preserved.

### Current tables

| Table | Purpose |
|---|---|
| `departments` | Organizational responsibility boundaries |
| `roles` | Admin-assigned user roles |
| `permissions` | Backend-authorized actions |
| `role_permissions` | Connects roles to permissions |
| `users` | Application user accounts |
| `user_roles` | Connects users to Admin-assigned roles |
| `ingestion_records` | Tracks controlled content submission, approval and indexing |

The database currently contains no default users, roles, departments or ingestion records.

Authentication, Admin role assignment and approval endpoints will be implemented as separate functionalities.

### SQLite concurrency

SQLite is configured with:

```text
PRAGMA foreign_keys=ON
PRAGMA journal_mode=WAL
PRAGMA busy_timeout=5000
```

These settings provide:

- Foreign-key enforcement
- Concurrent reading while a write is active
- A five-second wait when another write temporarily holds the database lock

SQLite supports multiple readers but only one writer at a time. PostgreSQL is recommended for a larger production deployment with many concurrent writes.

### Database versus FAISS

| SQLite | FAISS |
|---|---|
| Stores structured application records | Stores embedding vectors |
| Stores users, roles and workflow status | Performs semantic retrieval |
| Uses `rag_app.db` | Uses `index.faiss` and `index.pkl` |
| Does not perform vector search | Does not manage users or approvals |

FAISS has not yet been implemented.

### Database health

The FastAPI startup process:

```text
Load configuration
→ initialize missing tables
→ check the database connection
→ record database readiness
```

The `/health` endpoint reports:

```json
{
  "database": "available"
}
```

It does not expose the database URL, filename, credentials, table contents or raw exceptions.

### Test isolation

Automated database tests use temporary SQLite files managed by Pytest.

They do not insert test users, departments or ingestion records into the development `rag_app.db`.

## Health checks versus automated tests

Health checks and automated tests have different purposes.

- `/health` checks the running application's current component status.
- Pytest verifies that the code behaves as expected.
- LangSmith will later trace LangChain pipeline executions.

Tests should run before deployment, not during every production startup.

## Planned customer-safe response

When no approved answer is available, the customer-facing application will use:

```text
That's a thoughtful question and a valuable perspective. Thank you for
raising it. It will be taken into consideration as our guidance continues
to evolve.
```

The customer will not see:

- Private review workflow
- Similar-issue checks
- Similarity scores
- Internal approval or rejection status
- Policy Maker identity
- Internal notes
- Department assignment
- LangSmith traces

This customer-query functionality has not yet been implemented.

## Security

The following are excluded from Git:

- `.env`
- `venv/`
- Uploaded user documents
- Generated SQLite database files
- Generated FAISS files
- Python cache files
- Test cache files

Before committing changes, run:

```bat
git status --short
```

Confirm that `.env`, `venv/` and `rag_app.db` never appear.