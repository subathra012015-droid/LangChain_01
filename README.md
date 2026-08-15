# LangChain_01

A beginner-friendly, full-stack Retrieval-Augmented Generation application built incrementally with Python.

Each functionality is created, tested, validated and deployed locally before development proceeds to the next functionality.

## Current status

Completed:

- Functionality 0 — Project Foundation
- Functionality 1 — Health and System Status

The application currently provides:

- Python 3.11 virtual environment
- FastAPI backend
- Streamlit frontend
- Dynamic environment configuration
- FastAPI root endpoint
- FastAPI health endpoint
- Streamlit system-status display
- Safe unavailable-backend handling
- Automated backend and frontend tests
- Secure Git exclusions

The following features will be added separately:

- SQLite history database
- Multi-format document ingestion
- Text splitting
- Hugging Face embeddings
- FAISS vector storage and retrieval
- LangChain RAG pipeline
- OpenAI answer generation
- LangSmith tracing

## Project structure

```text
LangChain_01/
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── data/
│   └── uploads/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_frontend.py
│   └── test_main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The `.env` file and `venv/` folder exist locally but are intentionally excluded from Git.

The SQLite database and FAISS index will be generated only when their functionalities are implemented.

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
6 passed
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
  "database": "not_configured",
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

SQLite, FAISS and LangSmith will receive real health checks when their functionalities are implemented.

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

The frontend calls FastAPI’s `/health` endpoint and displays:

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

## Health checks versus automated tests

Health checks and automated tests have different purposes.

- `/health` checks the running application’s current component status.
- Pytest verifies that the code behaves as expected.
- LangSmith will later trace LangChain pipeline executions.

Tests should run before deployment, not during every production startup.

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

Confirm that `.env` never appears.