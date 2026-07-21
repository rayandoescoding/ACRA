# Run ACRA with Docker Compose

## Prerequisites

- Docker Desktop with Docker Compose v2 enabled

## Start the stack

1. Copy the environment template and replace its placeholder secrets.

   ```powershell
   Copy-Item .env.example .env
   ```

2. Build and start all services.

   ```powershell
   docker compose up --build
   ```

The frontend is available at `http://localhost:3000`, the backend API at `http://localhost:8000`, and the API documentation at `http://localhost:8000/docs`.

On startup, PostgreSQL becomes healthy first. The backend then runs `alembic upgrade head`, starts FastAPI, and performs its existing bootstrap and optional demo seed. The frontend starts only after the backend health check succeeds.

## Verify the stack

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-WebRequest http://localhost:3000
```

To verify authenticated API access, use the bootstrap credentials configured in `.env`:

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/auth/login -ContentType "application/json" -Body '{"email":"admin@example.com","password":"replace-with-a-strong-local-password"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Uri http://localhost:8000/api/v1/tickets -Headers $headers
```

To verify ticket processing, replace `<ticket-id>` with an ID returned by the ticket list request:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/tickets/<ticket-id>/process -Headers $headers
```

## Stop the stack

```powershell
docker compose down
```

Database data is retained in the `postgres_data` named volume. To remove the local database deliberately, run `docker compose down --volumes`.

## Environment notes

- `NEXT_PUBLIC_ACRA_API_BASE_URL` is embedded in the browser bundle during the frontend image build. For local Docker use, it must point to a browser-reachable backend URL such as `http://localhost:8000/api/v1`.
- PostgreSQL is reached internally by the backend at the Compose service hostname `postgres`.
- `.env` is ignored by Git; do not commit credentials.
