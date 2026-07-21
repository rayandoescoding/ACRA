# ACRA v1.0.0 release checklist

Use this checklist for the final release candidate and the v1.0.0 tag.

## Pre-release checklist

- [ ] Confirm the release scope contains only approved v1.0.0 work.
- [ ] Review open issues and document any deferred work in the roadmap.
- [ ] Confirm README, architecture, testing, Docker, deployment, and release documentation are current.
- [ ] Verify committed environment files contain placeholders only.
- [ ] Confirm generated artifacts, local environments, logs, and credentials are not staged for release.
- [ ] Review dependency changes and the lockfile.

## Testing checklist

- [ ] Run backend integration tests against a dedicated disposable PostgreSQL database.
- [ ] Run frontend component tests with `npm test` from `frontend/`.
- [ ] Run frontend type validation.
- [ ] Run `npm run build` from `frontend/`.
- [ ] Verify the Docker Compose stack starts and passes its health checks.
- [ ] Manually verify login, ticket list, ticket detail, processing, cleared guardrail, and human-review guardrail paths.

See [TESTING.md](TESTING.md) for the required backend database setup and exact test commands.

## Deployment checklist

- [ ] Create or select the managed PostgreSQL production database.
- [ ] Configure production backend variables in the chosen hosting provider.
- [ ] Configure the Vercel production API URL.
- [ ] Set `ALLOWED_ORIGINS` to the exact deployed frontend origin.
- [ ] Set a long, non-default `JWT_SECRET_KEY`.
- [ ] Set `ENVIRONMENT=production`, `DEBUG=false`, and `DEMO_SEED_ENABLED=false`.
- [ ] Run `alembic upgrade head` before serving production traffic.
- [ ] Configure `/api/v1/health` as the backend health-check endpoint.
- [ ] Remove bootstrap administrator credentials after the initial account is created.

See [DEPLOYMENT.md](DEPLOYMENT.md) for provider-neutral deployment and rollback procedures.

## Verification checklist

- [ ] Confirm `GET /api/v1/health` returns HTTP 200 from the deployed backend.
- [ ] Confirm the deployed frontend loads over HTTPS.
- [ ] Confirm login succeeds with a production operator account.
- [ ] Confirm authenticated ticket listing and ticket retrieval work.
- [ ] Confirm a ticket-processing request persists a resolution.
- [ ] Confirm browser requests do not report CORS errors.
- [ ] Confirm structured backend logs and processing metrics are emitted during a ticket-processing run.
- [ ] Record the deployed frontend URL, backend URL, database migration revision, and release timestamp.

## Version tagging checklist

- [ ] Set the release version to `v1.0.0` in release materials as appropriate.
- [ ] Ensure the working tree contains only intended release changes.
- [ ] Commit the verified release documentation and source state.
- [ ] Create an annotated Git tag: `git tag -a v1.0.0 -m "ACRA v1.0.0"`.
- [ ] Push the release commit and tag: `git push origin main --follow-tags`.
- [ ] Create release notes summarizing the operator console, authenticated processing pipeline, deployment guidance, and known limitations.
