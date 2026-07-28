#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
INGESTION_DB="/tmp/gli_ingestion_demo.db"
SERVER_PORT=8100
SERVER_URL="http://127.0.0.1:${SERVER_PORT}"
CONFIG_PATH="${REPO_ROOT}/configs/cloud_ingestion.yaml"

log()  { printf "\n\033[1;34m[demo]\033[0m %s\n" "$*"; }
ok()   { printf "\033[1;32m  ✓\033[0m %s\n" "$*"; }
fail() { printf "\033[1;31m  ✗\033[0m %s\n" "$*"; exit 1; }

cleanup() {
    if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        log "Stopping ingestion server (pid $SERVER_PID)"
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

log "Step 1/6: Writing local ingestion config"
mkdir -p "${REPO_ROOT}/configs"
cat > "$CONFIG_PATH" <<EOF
server:
  host: 127.0.0.1
  port: ${SERVER_PORT}
  workers: 1
  log_level: WARNING
database:
  url: sqlite:///${INGESTION_DB}
auth:
  enabled: false
  api_key: ""
cors:
  allowed_origins:
    - "*"
EOF
ok "Wrote ${CONFIG_PATH}"
rm -f "$INGESTION_DB"
ok "Cleared any previous demo DB at ${INGESTION_DB}"

log "Step 2/6: Checking Python deps"
python -c "import fastapi, uvicorn, pydantic, yaml" 2>/dev/null || pip install --quiet fastapi 'uvicorn[standard]' pydantic pyyaml
ok "Server deps present"

log "Step 3/6: Starting ingestion server on ${SERVER_URL}"
python -m cloud_ingestion.server > /tmp/gli_ingestion.log 2>&1 &
SERVER_PID=$!
for i in {1..20}; do
    if curl -sf "${SERVER_URL}/api/v1/health" >/dev/null 2>&1; then
        ok "Server is up (pid ${SERVER_PID})"; break
    fi
    sleep 0.5
done
if ! curl -sf "${SERVER_URL}/api/v1/health" >/dev/null 2>&1; then
    log "Server log tail:"; tail -30 /tmp/gli_ingestion.log
    fail "Server failed to start"
fi

log "Step 4/6: Turning telemetry on and doing a mock run"
gli-flow telemetry mode full > /dev/null 2>&1 || true

DESIGN="examples/counter"
if [[ ! -d "${REPO_ROOT}/${DESIGN}" ]]; then
    log "No examples/counter — using quickstart to create one"
    (cd "$REPO_ROOT" && echo "demo_design" | gli-flow quickstart) || true
    DESIGN="demo_design"
fi

log "Running: gli-flow run ${DESIGN} --mock"
gli-flow run "${DESIGN}" --mock 2>&1 | tail -20 || true

RUN_ID="$(python -c "
from gli_flow.database.sqlite import DatabaseManager
runs = DatabaseManager().get_runs(limit=1)
print(runs[0]['run_id'] if runs else '')
" 2>/dev/null)"

[[ -z "$RUN_ID" ]] && fail "No run_id found in local DB — the run didn't record."
ok "Newest run_id: ${RUN_ID}"

log "Step 5/6: Uploading telemetry to ${SERVER_URL}"
export GLI_SERVER_URL="${SERVER_URL}"
gli-flow telemetry upload-internal "$RUN_ID" || true

log "Step 6/6: Querying the ingestion DB"
echo ""; echo "── Server stats ──────────────────────────────────────────────"
curl -s "${SERVER_URL}/api/v1/stats" | python -m json.tool
echo ""; echo "── Upload audit rows ────────────────────────────────────────"
sqlite3 -header -column "$INGESTION_DB" \
    "SELECT run_id, telemetry_count, failures_count, status, ingested_at FROM upload_audit;" || echo "(none)"
echo ""; echo "── Telemetry event rows (first 10) ──────────────────────────"
sqlite3 -header -column "$INGESTION_DB" \
    "SELECT run_id, tool, stage, event, ingested_at FROM telemetry_events LIMIT 10;" || echo "(none)"
echo ""; echo "── Failure atlas rows (first 10) ────────────────────────────"
sqlite3 -header -column "$INGESTION_DB" \
    "SELECT run_id, tool, stage, failure_type, ingested_at FROM failure_atlas_events LIMIT 10;" || echo "(none)"

ok "Demo complete."
echo ""
echo "Ingestion DB: ${INGESTION_DB}"
echo "Server log:   /tmp/gli_ingestion.log"
