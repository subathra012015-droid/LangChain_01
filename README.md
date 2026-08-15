# LangChain_01

A beginner-friendly, full-stack Retrieval-Augmented Generation application built incrementally with Python.

Each functionality is created, tested, validated and deployed locally before development proceeds to the next functionality.

## Current status

Functionality 0 establishes the project foundation:

- Python 3.11 virtual environment
- FastAPI backend
- Streamlit frontend
- Dynamic environment configuration
- Automated testing with Pytest
- Secure Git exclusions

The following features will be added separately in later functionalities:

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
│   └── main.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── data/
│   └── uploads/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The `.env` file and `venv/` folder exist locally but are intentionally excluded from Git.

## Requirements

- Windows 11
- Python 3.11
- Git
- Visual Studio Code

## Create the virtual environment

From the project root:

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

Verify package compatibility:

```bat
python -m pip check
```

## Configure the application

Copy the variable names from `.env.example` into a local `.env` file.

Example local development configuration:

```env
APP_NAME=LangChain RAG Application
APP_ENV=development
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
BACKEND_URL=http://127.0.0.1:8000
DATABASE_URL=sqlite:///./rag_app.db
```

Supported `APP_ENV` values are:

- `development`
- `testing`
- `production`

Configuration values are loaded dynamically. They are not hard-coded in Python.

Never commit `.env` or place API keys in source code.

## Run automated tests

```bat
python -m pytest -v
```

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

## Run the Streamlit frontend

Keep the backend running and open Terminal 2:

```bat
venv\Scripts\activate
python -m streamlit run frontend\app.py --server.address 127.0.0.1 --server.port 8501
```

Frontend:

```text
http://127.0.0.1:8501
```

Stop either local server using:

```text
Ctrl+C
```

## Security

The following files and folders are excluded from Git:

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