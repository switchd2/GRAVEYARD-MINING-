# ☠ Graveyard Mining — AI Risk Intelligence for Open-Source Architecture

[![Backend CI](https://github.com/switchd2/GRAVEYARD-MINING-/actions/workflows/ci.yml/badge.svg)](https://github.com/switchd2/GRAVEYARD-MINING-/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.1-000000.svg?style=flat&logo=next.js)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?style=flat&logo=supabase)](https://supabase.com)
[![Railway](https://img.shields.io/badge/Railway-Backend-0B0D0E.svg?style=flat&logo=railway)](https://railway.app)
[![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000.svg?style=flat&logo=vercel)](https://vercel.com)

**Graveyard Mining** is an evidence-based risk assessment platform that mines abandoned GitHub repositories, diagnoses why they failed using GPT-4o-mini, performs security audits via OSV and Socket, and generates risk-armored 5-phase project roadmaps before writing code.

---

## 🏛 System Architecture

```text
               +----------------------------------+
               |        Users / Web Client        |
               +----------------------------------+
                                |
                                | HTTPS
                                v
               +----------------------------------+
               |      Vercel (Next.js 14 UI)      |
               +----------------------------------+
                                |
                                | REST API (JSON)
                                v
               +----------------------------------+
               |     Railway (FastAPI Service)    |
               |                                  |
               |  - SlowAPI Rate Limiter          |
               |  - Gunicorn Multi-Worker         |
               |  - AnalysisService Pipeline      |
               +----------------------------------+
                  /             |              \
                 /              |               \
                v               v                v
     +---------------+  +---------------+  +------------------------+
     | OpenAI API    |  | GitHub API    |  | Supabase PostgreSQL    |
     | GPT-4o-mini   |  | Search/Triage |  | Transaction Pooler     |
     | Embeddings    |  | Tavily Web    |  | Alembic Migrations     |
     +---------------+  +---------------+  +------------------------+
```

---

## 📁 Repository Structure

```text
├── backend/
│   ├── alembic/              # Database migration scripts
│   ├── api/
│   │   └── routes.py         # Thin FastAPI route handlers
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM schemas
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── services/
│   │   ├── ai_service.py       # OpenAI LLM diagnoses, embeddings & roadmaps
│   │   ├── analysis_service.py # Core pipeline orchestrator
│   │   ├── github_service.py   # GitHub REST API & Tavily context
│   │   ├── security_service.py # OSV/Libraries.io/Socket security checks
│   │   ├── report_service.py   # DB persistence & JSON serialization
│   │   ├── repo_triage.py      # Abandonment scoring heuristics
│   │   └── clustering.py       # KMeans failure vector clustering
│   ├── app.py                # FastAPI entry point & security middleware
│   ├── database.py           # SQLAlchemy engine configuration
│   ├── logging_config.py     # Centralized structured logger
│   ├── Dockerfile            # Multi-stage production container
│   ├── railway.toml          # Railway platform deployment spec
│   ├── alembic.ini           # Migration configuration
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── app/                  # Next.js App Router pages
│   ├── components/           # UI components (Dashboard, Form, Roadmap)
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.js    # Tailwind styling rules
├── .github/workflows/ci.yml # GitHub Actions CI pipeline
├── start.ps1                 # Single-command local dev launcher
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Node.js 18+
- PowerShell (Windows)

### 1-Command Launcher (Native / Local Python)

Run both backend (`http://localhost:8000`) and frontend (`http://localhost:3000`) concurrently with live color-coded logs:

```powershell
.\start.ps1
```

Flags available:

- `.\start.ps1 -BackendOnly` — Run FastAPI backend only
- `.\start.ps1 -FrontendOnly` — Run Next.js frontend only
- `.\start.ps1 -NoBrowser` — Suppress auto-opening the browser

---

## 🐳 Docker Quick Start (PostgreSQL + pgAdmin)

Spin up the entire stack (PostgreSQL 16, pgAdmin 4, FastAPI Backend, Next.js Frontend) with a single command:

### 1. Copy Environment Template
```bash
cp .env.example .env
```
Update `.env` with your `OPENAI_API_KEY` and optional `GITHUB_TOKEN`.

### 2. Start Containers
```bash
docker compose up --build
```

### 3. Service Access
| Service | URL | Credentials |
| --- | --- | --- |
| **Next.js Frontend** | `http://localhost:3000` | N/A |
| **FastAPI Backend** | `http://localhost:8000` | N/A |
| **Swagger API Docs** | `http://localhost:8000/docs` | N/A |
| **pgAdmin 4** | `http://localhost:5050` | `admin@example.com` / `admin` |
| **PostgreSQL DB** | `localhost:5432` | `postgres` / `postgres` / DB: `graveyard_mining` |

> **Note on Database Portability:** The backend detects `DATABASE_URL`. Switching from local Docker PostgreSQL to Railway or Supabase PostgreSQL requires changing only the `DATABASE_URL` environment variable. SQLite is retained as a fallback for lightweight development when `DATABASE_URL` is omitted.

---

## 🔑 Environment Variables Reference

Copy `.env.example` in `backend/` and `frontend/`:

### Backend (`backend/.env`)

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | PostgreSQL URI (`postgresql://...`) or local SQLite (`sqlite:///./graveyard_mining.db`) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o-mini diagnosis & embeddings |
| `GITHUB_TOKEN` | Recommended | GitHub Personal Access Token (increases rate limit from 60 to 5000 req/hr) |
| `TAVILY_API_KEY` | Optional | Tavily Web Search API key for repo post-mortem context |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins (e.g. `http://localhost:3000,https://app.vercel.app`) |
| `SENTRY_DSN` | Optional | Sentry monitoring DSN |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Yes | Full URL of the backend service (e.g. `https://api.up.railway.app` or `http://localhost:8000`) |

---

## 🗄 Database Setup & Migrations (Alembic)

The application uses SQLAlchemy with Alembic migration support. In Docker, migrations run automatically on startup via `entrypoint.sh`.

### Manual Migration Commands

```bash
cd backend
alembic upgrade head
```

### Generate a New Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new column"
```

---

## 🚀 Production Deployment Guide

### 1. Database (Supabase PostgreSQL)

1. Create a project at [supabase.com](https://supabase.com).
2. Navigate to **Project Settings** → **Database** → **Connection String** → **URI**.
3. Copy the transaction pooler connection string and set `DATABASE_URL` in Railway.

### 2. Backend (Railway)

1. Connect your GitHub repository to [Railway](https://railway.app).
2. Select the `backend/` directory for deployment.
3. Railway auto-detects `Dockerfile` or `railway.toml`.
4. Add environment variables under Railway service settings.

### 3. Frontend (Vercel)

1. Import repository on [Vercel](https://vercel.com).
2. Set root directory to `frontend`.
3. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `https://<your-railway-backend-url>`

---

## 📡 API Endpoints

| Method | Endpoint | Description | Rate Limit | Reasoning |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Health check endpoint | Unlimited | Unthrottled system monitoring |
| `GET` | `/` | Root API metadata | Unlimited | Lightweight metadata |
| `POST` | `/api/analyze` | Execute full project risk analysis | 7 req / min | Heavy GitHub API + OpenAI LLM + DB write pipeline |
| `GET` | `/api/analyses` | List recent project analyses | 40 req / min | Read-only lightweight DB queries |
| `GET` | `/api/analysis/{id}` | Get specific analysis report by ID | 40 req / min | Read-only report lookup |

---

## ✅ Deployment Verification

Verify production setup after deployment:

```bash
# 1. Health Check
curl -I https://your-backend.up.railway.app/health
# Expected: HTTP/1.1 200 OK -> {"status": "ok"}

# 2. Open Swagger Documentation
https://your-backend.up.railway.app/docs
```
