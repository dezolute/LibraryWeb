# LibraryWeb

If you want to test LibraryWeb you must have [Docker](https://docs.docker.com/desktop/setup/install/windows-install/)

Setup LibraryWeb in docker

```bash
docker compose -f ./docker-compose.yml -p libraryweb up -d
```

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧪 [SQLAlchemy](https://www.sqlalchemy.org/) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 🧰 [Alembic](https://alembic.sqlalchemy.org/en/latest/) for the Python creatin migrations.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 🚢 Deployment instructions using Docker Compose.
