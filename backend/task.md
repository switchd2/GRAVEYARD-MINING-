# Execution Checklist

- [x] Update implementation plan (PostgreSQL + pgAdmin confirmed)
- [x] 1. `backend/api/routes.py` — rate limit decorators
- [x] 2. `backend/Dockerfile` — HEALTHCHECK + EXPOSE + entrypoint
- [x] 3. `backend/entrypoint.sh` — wait-for-pg + alembic + gunicorn
- [x] 4. `backend/.dockerignore`
- [x] 5. `frontend/Dockerfile` — multi-stage Next.js
- [x] 6. `frontend/.dockerignore`
- [x] 7. `docker-compose.yml` — postgres + pgadmin + backend + frontend
- [x] 8. `.env.example` (root-level, Compose-aware)
- [x] 9. `README.md` — Docker section + corrected rate limit table
