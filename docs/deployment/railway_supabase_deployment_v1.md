# Railway + Supabase Deployment v1

**Generated:** 2026-06-23
**Goal:** Deploy GLI-FLOW backend on Railway with Supabase PostgreSQL as the database.

---

## Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Railway   │────▶│  GLI-FLOW    │────▶│    Supabase      │
│  (FastAPI)  │     │  Backend     │     │  PostgreSQL      │
└─────────────┘     └──────────────┘     └─────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Upload Queue│
                   │  (in-memory  │
                   │   or file)   │
                   └──────────────┘
```

## Prerequisites

- Railway account with billing enabled
- Supabase project (free tier works for prototyping)
- `DATABASE_URL` from Supabase project settings → Database → Connection string (use the **Pooled** connection `:6543`)

## Step 1: Supabase Project Setup

```bash
# Create a Supabase project via dashboard or CLI
# Then get your connection string from:
# Project Settings → Database → Connection Pooling → URI

# Format (pooled, recommended for Railway):
# postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

### Required PostgreSQL Extensions

```sql
-- Run in Supabase SQL Editor or via psql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- query performance
```

## Step 2: Railway Service Configuration

```bash
# 1. Create a new Railway project
# 2. Connect your GitHub repo (gli-flow-asic)
# 3. Add a PostgreSQL service (or use external Supabase URL)
# 4. Set the start command:
```

### railway.json

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python -m gli_flow.backend.server",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 10,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## Step 3: Environment Variables

Set these in Railway Dashboard → Variables:

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | `postgresql://postgres.<ref>:<password>@pooler.supabase.com:6543/postgres` | Yes |
| `GLI_FLOW_BACKEND_PORT` | `8080` | Yes (Railway assigns `$PORT`) |
| `CORS_ORIGINS` | `https://your-frontend.railway.app` | Yes |
| `BHARATCODE_API_KEY` | `sk-...` | Only if AI features needed |

**Important:** Railway injects `$PORT` automatically. The server must bind to `0.0.0.0:$PORT`.

## Step 4: Database Migration

```bash
# After deployment connects, run the migration:
# Option A: Via Railway Exec
railway run python scripts/migrate_sqlite_to_postgres.py

# Option B: One-shot command in Railway dashboard
python scripts/migrate_sqlite_to_postgres.py --batch-size 500 --commit-interval 1000
```

### Post-Migration Validation

```bash
python scripts/validate_postgres_migration.py --strict
```

## Step 5: Health Check & Monitoring

The backend exposes:

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check (returns status, db provider, queue stats) |
| `GET /metrics` | Prometheus metrics (if configured) |
| `GET /debug/db` | Database provider info + connection status |

### Railway Health Check Config

```
Path: /health
Period: 10s
Timeout: 5s
Threshold: 3 failures
```

## Connection Pooling

| Setting | Recommendation |
|---------|---------------|
| Pool size | 5-10 connections |
| Pool timeout | 30 seconds |
| Max overflow | 2 |

Supabase free tier allows **15 connections max**. The pooler at `:6543` handles up to 200 pooled connections (Starter plan).

## Rollback Procedure

```bash
# 1. Unset DATABASE_URL → reverts to SQLite
# 2. Restart Railway service
# 3. Validate with /health endpoint

# If data was migrated and SQLite is stale:
#   - Keep DATABASE_URL set
#   - Run reverse migration (pg → sqlite) if needed
```

## Security

- Store `DATABASE_URL` as a Railway secret (encrypted at rest)
- Use Supabase's **PgBouncer** connection pooler (`:6543`) for production
- Enable **SSL enforcement** in Supabase dashboard
- Never expose `DATABASE_URL` in client-side code
- Use Supabase **Row Level Security** for direct client queries

## Cost Estimation (Monthly)

| Service | Free Tier | Pro Tier |
|---------|-----------|----------|
| Railway | $5 (includes 500 hours) | $20 |
| Supabase | Free (500 MB DB, 2 GB bandwidth) | $25 |
| **Total** | **$5** | **$45** |

Free tier is sufficient for prototyping and low-traffic production.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `could not connect to server` | Wrong `DATABASE_URL` or network | Verify URL, check Supabase dashboard → Database |
| `SSL connection required` | SSL not enabled | Append `?sslmode=require` to `DATABASE_URL` |
| `too many connections` | Pool size too large | Reduce pool size in PostgresProvider |
| `permission denied` | Wrong credentials | Reset password in Supabase dashboard |
| `relation does not exist` | Migration not run | Run migration script |
