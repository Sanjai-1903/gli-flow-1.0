# Multi-tenant deployment — what to do on your machine

This is the runbook for the human-only steps needed to bring up the new
per-user auth stack. Everything code-side is already written; these are the
steps that need your accounts and your credentials.

## 1. Apply the Phase 1 migration to Supabase

```
cd ~/gli-flow-1.0/gli-flow-asic
pip3 install psycopg2-binary                       # once
export GLI_DATABASE_URL="postgresql://postgres.cniloojatepkqaicvbig:gli-flow-pilot@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
python3 scripts/apply_phase1_migration.py
```

Expected: "OK: all Phase 1 tables and columns present" plus row counts
showing 1 in `app_users` (legacy user) and 90-ish in the ingestion tables
(backfilled to legacy user).

## 2. Enable Google sign-in in Supabase

1. Supabase dashboard → **Authentication → Providers → Google → Enable**.
2. Follow the "Set up Google OAuth" link on that page — it opens Google
   Cloud Console. Create an OAuth 2.0 Client ID (application type: Web
   application). Authorised redirect URIs:
   - `https://cniloojatepkqaicvbig.supabase.co/auth/v1/callback`
3. Paste the Google Client ID + Client Secret back into Supabase.
4. Supabase dashboard → **Project Settings → API** → copy:
   - `Project URL` → `VITE_SUPABASE_URL`, `SUPABASE_URL`
   - `anon public` key → `VITE_SUPABASE_ANON_KEY`
   - `JWT Secret` → `SUPABASE_JWT_SECRET` (this is the important one for
     the ingest server — don't confuse it with the anon key)

## 3. Local smoke test (no deploys yet)

Verifies migration + ingest server + Bearer auth work end-to-end against
Supabase, without needing Vercel or Google OAuth set up.

Terminal A — start the ingest server pointed at Supabase:
```
cd ~/gli-flow-1.0/gli-flow-asic
export GLI_DATABASE_URL="postgresql://..."           # same URL as step 1
export SUPABASE_JWT_SECRET="paste from step 2"       # only needed for browser paths
python3 -m uvicorn cloud_ingestion.server:create_app --factory --port 8100
```

Terminal B — run the smoke test:
```
cd ~/gli-flow-1.0/gli-flow-asic
export GLI_DATABASE_URL="postgresql://..."
python3 scripts/smoke_test_phase1_auth.py
```

Expected: 9 green ticks and "All smoke tests passed." If any step fails,
stop and share the output — nothing beyond this point works without this
passing.

## 4. Deploy the ingest server to Render

Requires: GitHub push access. (Blocked until Jegadiswar adds you to the
repo, or you fork it. Same blocker as before.)

Once unblocked:

1. Push all the changes: `git add -A && git commit -m "phase 1-7: multi-tenant + auth" && git push`.
2. Render dashboard → **New → Blueprint** → connect the repo. Render reads
   `render.yaml` and offers to create the service.
3. In the service's Environment tab, add secrets:
   - `GLI_DATABASE_URL` = the Supabase URL from step 1
   - `SUPABASE_JWT_SECRET` = from step 2
   - `GLI_WEB_URL` = your Vercel URL (once you have it), e.g. `https://gli-flow.vercel.app`
4. Deploy. Note the public URL Render assigns you, e.g.
   `https://gli-flow-ingest.onrender.com`.

## 5. Deploy the dashboard to Vercel

1. `cd dashboard && cp .env.example .env.local`. Fill in the three vars
   from step 2 and set `VITE_INGEST_URL` to the Render URL from step 4.
2. `npm install` (adds `@supabase/supabase-js`) then `npm run dev` to sanity-check locally.
3. Vercel dashboard → **Add New → Project** → import the GitHub repo.
   - Root directory: `dashboard`
   - Framework preset: Vite (auto-detected)
   - Environment variables: paste the same three `VITE_*` vars + `VITE_INGEST_URL`
4. Deploy. Grab the Vercel URL, e.g. `https://gli-flow.vercel.app`.
5. Back to Render: update `GLI_WEB_URL` to the Vercel URL so device-flow
   verification URIs point at the right place.
6. Back to Supabase → Authentication → URL Configuration → add
   `https://gli-flow.vercel.app` to Site URL and Additional Redirect URLs.

## 6. Full end-to-end test

On your Mac:
```
export GLI_INGEST_URL="https://gli-flow-ingest.onrender.com"
export GLI_WEB_URL="https://gli-flow.vercel.app"

gli-flow login                # opens browser, sign in with Google, approve code
gli-flow whoami               # should print your email + user_id
gli-flow run examples/counter --mock
gli-flow sync-status          # shows the run enqueued
gli-flow sync                 # or wait for the auto-sync hook
```

Then open the Vercel dashboard: your run should appear in the runs list,
scoped to your account only. Sign in as another Google account (a second
student simulation): you should see zero runs — that's RLS working.

## Files added in this phase (for your review)

- `gli_flow/database/pg_migrations_phase1_multitenant.py` — the migration
- `gli_flow/cloud/auth.py` — CLI-side token storage + device flow
- `gli_flow/cloud/sync.py` — offline-first sync + 7-day retention
- `gli_flow/cli/auth_commands.py` — `login`, `logout`, `whoami`, `sync`
- `cloud_ingestion/auth.py` — Bearer token validation
- `cloud_ingestion/supabase_jwt.py` — Supabase JWT validation for browser
- `cloud_ingestion/routes_cli.py` — device flow + token endpoints
- `dashboard/src/lib/supabase.js` — Supabase client
- `dashboard/src/AuthGate.jsx` — sign-in gate
- `dashboard/src/CliTokensPage.jsx` — token management UI
- `dashboard/src/DeviceApprovalPage.jsx` — device-flow approval UI
- `dashboard/vercel.json`, `dashboard/.env.example` — deploy config
- `scripts/apply_phase1_migration.py` — migration runner
- `scripts/smoke_test_phase1_auth.py` — end-to-end smoke test

## Known open items

- `web/package.json` — leftover placeholder from a scrapped Next.js
  approach. Safe to delete: `rm -rf web/`.
- Password strength: your Supabase Postgres password is still `gli-flow-pilot`.
  Rotate it in Supabase → Project Settings → Database, then update the
  `GLI_DATABASE_URL` secret in Render.
