# Automated testing

## Backend integration tests

Backend tests require a dedicated disposable PostgreSQL database. They refuse to run without `ACRA_TEST_DATABASE_URL` and never use the normal development database.

With the Docker Compose PostgreSQL service running, create a separate test database once:

```powershell
docker compose exec postgres createdb -U acra acra_test
```

Install the test dependencies and run the suite:

```powershell
cd backend
python -m pip install -r requirements-test.txt
$env:ACRA_TEST_DATABASE_URL = "postgresql+asyncpg://acra:replace-with-a-local-database-password@localhost:5432/acra_test"
pytest
```

The test fixture recreates the schema for each test and drops it afterward. Do not point `ACRA_TEST_DATABASE_URL` at a database containing data you need to keep.

## Frontend component tests

```powershell
cd frontend
npm test
```

## Complete suite

Run the backend suite first, then the frontend suite:

```powershell
cd backend
$env:ACRA_TEST_DATABASE_URL = "postgresql+asyncpg://acra:replace-with-a-local-database-password@localhost:5432/acra_test"
pytest

cd ..\frontend
npm test
```
