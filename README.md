Backend for Sanitation Operators Project

Quick start (local - venv)

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Start the API (SQLite, default):

```bash
uvicorn backend.app.main:app --reload --port 8000
```

3. Endpoints:
- `POST /auth/register` (protected: only `system` or `admin` can create users)
- `POST /auth/login`
- `POST /auth/init` (dev only: create initial system user)
- `GET /health`
- `/companies` CRUD (protected)


Using Docker Compose (recommended for testing Postgres integration)

1. Create a `.env` file at repo root with these variables:

```
POSTGRES_DB=sanitation
POSTGRES_USER=appadmin
POSTGRES_PASSWORD=admin1234
DATABASE_URL=postgresql://appadmin:admin1234@db:5432/sanitation
ADMIN_USERNAME=system
ADMIN_PASSWORD=system1234
ADMIN_ROLE=system
```

2. Start services:

```bash
docker compose -f docker-compose.dev.yml up --build
```

3. The backend will automatically create the initial `system` user (from `ADMIN_USERNAME` env var) on startup.

4. Access Swagger docs: http://localhost:8000/docs


Which environment to use?
- Use **Docker Compose** when you want to test integration with Postgres and simulate production-like environment (recommended for end-to-end testing).
- Use **venv** (SQLite) for fast local iteration and unit tests.

Seeding initial system user on startup
- If you set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and optionally `ADMIN_ROLE` in the environment, the backend will create that user on startup (if it does not exist).
- `ADMIN_ROLE` can be `system`, `admin`, or `user` (default `system`).
- **Important for development**: Both `.env` and `docker-compose.dev.yml` must include these variables so they're passed to the container.

For testing without seed
- Use the `POST /auth/init` endpoint (dev only):
  ```bash
  curl -X POST http://localhost:8000/auth/init \
    -H "Content-Type: application/json" \
    -d '{"username":"system","password":"system1234"}'
  ```

Deploying to AWS (or production)

**Option 1: Use environment variables at container startup** (recommended)
- Set `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_ROLE` as environment variables in your ECS task definition, Lambda env vars, or CloudFormation parameters.
- The backend lifespan function will automatically create the user on first startup.
- Example (ECS):
  ```json
  "environment": [
    {"name": "DATABASE_URL", "value": "postgresql://user:pass@rds-host:5432/db"},
    {"name": "ADMIN_USERNAME", "value": "system"},
    {"name": "ADMIN_PASSWORD", "value": "<secure-password>"},
    {"name": "ADMIN_ROLE", "value": "system"}
  ]
  ```

**Option 2: Use AWS Secrets Manager** (more secure)
- Store `ADMIN_PASSWORD` in Secrets Manager.
- Pass the secret ARN and retrieve it in `app/main.py` using boto3.

**Option 3: Manual initialization** (fallback)
- If the initial user doesn't exist, use the `/auth/init` endpoint from admin CLI or a setup script.
- Ensure you have a way to reach the API from a bastion host or VPN.

**Option 4: Terraform/CloudFormation post-deployment script**
- After infrastructure is deployed, run a Lambda or ECS task that calls `/auth/init` to create the system user.

**Best practice for production:**
- Use environment variables (Option 1) + AWS Secrets Manager (Option 2) for maximum security.
- Never commit production credentials to Git.
- Rotate the initial system password after first login.

Security note
- Replace the `SECRET_KEY` in `backend/app/core/security.py` with a secure value from environment variables in production.
- Use strong passwords (min. 8 chars, alphanumeric + special chars) for production deployments.


