# ACRA v1.0 deployment

ACRA can be deployed with a managed PostgreSQL database, a container-hosted FastAPI backend, and a Vercel-hosted Next.js frontend. The application remains provider-neutral: use Railway or Render for the backend and Railway PostgreSQL, Neon, or an equivalent managed PostgreSQL service for the database.

## Deployment architecture

```text
Browser
  -> Vercel (Next.js frontend)
  -> Railway or Render (FastAPI container, /api/v1)
  -> Managed PostgreSQL
```

The frontend calls `NEXT_PUBLIC_ACRA_API_BASE_URL`. The backend allows that frontend origin through `ALLOWED_ORIGINS`, authenticates with its configured JWT secret, and connects to PostgreSQL through `DATABASE_URL`.

## Environment separation

| Environment | Configuration source | Purpose |
| --- | --- | --- |
| Local development | `backend/.env` and `frontend/.env.local`, based on their `.env.example` files | Run services directly on a workstation. |
| Local Docker | Root `.env`, based on `.env.example` | Run the Docker Compose stack. |
| Production | Deployment-provider environment settings, using the production example files as references | Deploy managed services without committing secrets. |

Do not commit `.env`, `.env.local`, `.env.production`, or provider-exported secret files. The example files contain placeholders only.

## Required environment variables

### Backend

| Variable | Required | Production value |
| --- | --- | --- |
| `APP_NAME` | Yes | `ACRA` |
| `APP_VERSION` | Yes | `1.0.0` |
| `ENVIRONMENT` | Yes | `production` |
| `DEBUG` | Yes | `false` |
| `HOST` | Yes | `0.0.0.0` |
| `PORT` | Yes | Platform-provided port, or `8000` when the platform does not provide one. |
| `ALLOWED_ORIGINS` | Yes | JSON array containing the exact Vercel origin, for example `["https://your-project.vercel.app"]`. |
| `DATABASE_URL` | Yes | Managed PostgreSQL async URL: `postgresql+asyncpg://user:password@host:5432/database?ssl=require`. |
| `JWT_SECRET_KEY` | Yes | Long, randomly generated secret stored only by the provider. |
| `JWT_ALGORITHM` | Yes | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | `60`, or the approved policy value. |
| `AUTH_BOOTSTRAP_ADMIN_EMAIL` | First deployment only | Initial administrator email; remove after bootstrap succeeds. |
| `AUTH_BOOTSTRAP_ADMIN_PASSWORD` | First deployment only | Strong one-time password; remove after bootstrap succeeds. |
| `DEMO_SEED_ENABLED` | Yes | `false` unless an intentional production demonstration requires seed data. |

### Frontend

| Variable | Required | Production value |
| --- | --- | --- |
| `NEXT_PUBLIC_ACRA_API_BASE_URL` | Yes | Public backend URL ending in `/api/v1`, for example `https://api.example.com/api/v1`. |

`NEXT_PUBLIC_*` variables are public browser configuration. Never place secrets in them. Vercel applies this API URL during the frontend build, so redeploy the frontend after changing it.

## Database setup and migrations

1. Create a managed PostgreSQL database and obtain its connection details.
2. Convert its connection string to the required `postgresql+asyncpg://` form. Percent-encode reserved characters in credentials.
3. Set `DATABASE_URL` in the backend deployment environment. Enable the provider's required SSL option, commonly `?ssl=require`.
4. Before the first backend release, run the migration command from the backend release environment:

   ```bash
   alembic upgrade head
   ```

5. Confirm that the migration succeeds before serving production traffic.

The existing backend container also runs `alembic upgrade head` before Uvicorn starts. This makes normal redeploys idempotent. Run migrations as a one-off pre-deployment step before scaling to multiple backend instances.

## Backend deployment: Railway or Render

1. Create a new web service from this repository and set the service root directory to `backend`.
2. Select Dockerfile-based deployment; the existing `backend/Dockerfile` is the build definition.
3. Add every backend variable listed above through the provider's environment or secret configuration UI.
4. Configure the managed PostgreSQL `DATABASE_URL`, exact Vercel `ALLOWED_ORIGINS`, a new `JWT_SECRET_KEY`, `DEBUG=false`, and `DEMO_SEED_ENABLED=false`.
5. Run `alembic upgrade head` as the pre-deployment migration step.
6. Deploy one backend instance. The existing container startup command is:

   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
   ```

7. Configure the provider health check path as `/api/v1/health`.
8. Open `https://<backend-domain>/api/v1/health` and confirm a `healthy` response.

The provider supplies the public backend domain. Use HTTPS in the frontend API URL.

## Frontend deployment: Vercel

1. Import the repository into Vercel and set the root directory to `frontend`.
2. Use the detected Next.js framework settings and the existing `npm run build` build command.
3. Set `NEXT_PUBLIC_ACRA_API_BASE_URL` to `https://<backend-domain>/api/v1` for Production.
4. Deploy the frontend.
5. Copy the resulting Vercel production URL into the backend `ALLOWED_ORIGINS` JSON array, redeploy the backend, then redeploy the frontend if its API URL changed.
6. Verify login, ticket retrieval, and ticket processing against the deployed backend.

## Production readiness checklist

- [ ] Managed PostgreSQL is created, reachable by the backend, and uses encrypted connections.
- [ ] `DATABASE_URL` uses `postgresql+asyncpg://` and contains no unencoded reserved credential characters.
- [ ] `alembic upgrade head` completed successfully against the production database.
- [ ] Backend has `ENVIRONMENT=production`, `DEBUG=false`, and a non-default `JWT_SECRET_KEY`.
- [ ] `ALLOWED_ORIGINS` contains only the exact deployed Vercel origin(s).
- [ ] `DEMO_SEED_ENABLED=false`, unless approved otherwise.
- [ ] Bootstrap administrator credentials have been removed after the administrator account was created.
- [ ] `NEXT_PUBLIC_ACRA_API_BASE_URL` points to the HTTPS backend URL ending in `/api/v1`.
- [ ] Backend health endpoint returns HTTP 200 at `/api/v1/health`.
- [ ] Login, authenticated ticket listing, ticket retrieval, and ticket processing have been manually verified.
- [ ] No secret exists in Git, Vercel public variables, frontend source, or committed environment files.

## Rollback procedure

1. Stop traffic to the failed release using the hosting provider's rollback or previous-deployment promotion feature.
2. Restore the previously known-good backend and/or Vercel deployment.
3. Verify `/api/v1/health`, login, and an authenticated ticket request.
4. Do not roll database migrations back automatically. Review the migration and data impact first; restore from the managed PostgreSQL backup only through an approved recovery procedure.
5. Record the failed release version, relevant logs, and the database migration revision before attempting another deployment.

## Post-deployment verification

```bash
curl https://<backend-domain>/api/v1/health
```

Then log in through the deployed Vercel application and confirm that the browser can retrieve tickets. A browser CORS failure indicates that `ALLOWED_ORIGINS` does not exactly match the frontend origin.
