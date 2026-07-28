# Supabase Connectivity Validation v1

**Generated:** 2026-06-23
**Script:** `scripts/test_supabase_connection.py`

---

## Purpose

Validate that GLI-FLOW can connect to a PostgreSQL (Supabase) database before any application code is modified.

## Requirements

- Read `DATABASE_URL` from environment
- Connect using `psycopg2`
- Execute diagnostic queries
- Exit non-zero on failure

## Test Script

```bash
DATABASE_URL="postgresql://user:pass@host:5432/db" python scripts/test_supabase_connection.py
```

### Tests Performed

1. **`SELECT version()`** — Confirm PostgreSQL server version
2. **`SELECT NOW()`** — Confirm server time and timezone
3. **`SELECT current_database()`** — Confirm database name
4. **Connection parameters** — Host, port, user, SSL status
5. **Schema introspection** — List existing tables in `public` schema

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Connection failed (bad URL, auth, network) |
| 2 | Query execution failed |

## Expected Results (Fresh Supabase Instance)

```
=== Test 1: SELECT version() ===
  PostgreSQL version: PostgreSQL 15.x ...

=== Test 2: SELECT NOW() ===
  Server time: 2026-06-23 HH:MM:SS.SSSSSS+00

=== Test 3: SELECT current_database() ===
  Current database: postgres (or your DB name)

=== Test 4: Connection Info ===
  Host: aws-0-xxx.pooler.supabase.com
  Port: 6543
  User: postgres.xxxxx
  Database: postgres
  SSL in use: True

=== Test 5: Schema Introspection ===
  No tables found in public schema (expected for fresh DB).

✓ All Supabase connectivity checks passed.
```

## Connection String Format

For Supabase:
```
postgresql://postgres.<project-ref>:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `could not connect to server` | Wrong host/port or network blocked | Verify Supabase connection string in project settings |
| `FATAL: password authentication failed` | Wrong password | Reset password in Supabase dashboard |
| `SSL connection required` | Supabase requires SSL | Append `?sslmode=require` to connection string |
| `database "postgres" does not exist` | Wrong database name | Use the database name from Supabase dashboard |
