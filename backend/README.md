# ACRA - Backend Service

Autonomous Multi-Agent Customer Resolution Platform (ACRA) backend project skeleton.

## Directory Structure

```text
backend/
│
├── app/
│   ├── main.py                # App entrypoint and routes
│   ├── core/
│   │   ├── config.py          # Settings and environment variables
│   │   ├── logging.py         # Logging configuration
│   │   └── __init__.py
│   ├── api/                   # API routers and endpoints
│   ├── models/                # Database models
│   ├── agents/                # AI multi-agent logic
│   ├── services/              # Business services
│   ├── schemas/               # Pydantic validation schemas
│   ├── orchestrator/          # Agent coordinator/orchestrator
│   ├── observability/         # Observability, tracing, and metrics
│   └── __init__.py
│
├── requirements.txt           # Project dependencies
└── README.md                  # This documentation file
```

## Setup & Running

### Prerequisites

- Python 3.12+

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
- GET `/`: Returns project status.
