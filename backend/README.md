# ACRA backend

The ACRA backend is a FastAPI service that provides authenticated ticket operations, the AI processing pipeline, persistence, and observability.

## Run locally

From this directory, configure `backend/.env` from `backend/.env.example`, install dependencies, then start the application:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `/docs` and health status at `/api/v1/health`.

## Related documentation

- [Project overview](../README.md)
- [Architecture](../ARCHITECTURE.md)
- [Testing](../TESTING.md)
- [Docker Compose](../DOCKER.md)
- [Production deployment](../DEPLOYMENT.md)
- [Release checklist](../RELEASE.md)
