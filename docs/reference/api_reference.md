# API Reference

All 79 endpoints defined in `backend/server.py`. Base URL: `http://127.0.0.1:8000`

## Runs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/runs` | List runs (limit, important filter) |
| GET | `/runs/count` | Total run count |
| GET | `/live_runs` | Currently running runs |
| GET | `/trends` | QoR/runtime trend (IMPROVING/DEGRADING/STABLE) |
| GET | `/runs/{run_id}` | Single run detail with artifacts, DRC, STA, telemetry |
| GET | `/runs/{run_id}/drc` | DRC combined result and analysis |
| GET | `/runs/{run_id}/image/{image_name}` | Serve layout images (webp/png/jpg) |
| GET | `/runs/{run_id}/report/{report_type}` | Serve report files (rpt/txt/csv/json/log) |
| GET | `/runs/{run_id}/artifacts` | List all artifacts in run directory |
| GET | `/runs/{run_id}/artifact` | Serve a single artifact file |
| GET | `/runs/{run_id}/artifact/preview` | Text preview of an artifact |
| GET | `/releases` | Top 10 release candidates by QoR |
| GET | `/health` | System health (DB + tool availability) |
| PATCH | `/runs/{run_id}/important` | Toggle important flag on a run |
| GET | `/runs/{run_id}/diff/{previous_run_id}` | Field-by-field run comparison |
| GET | `/runs/{run_id}/compare/{other_run_id}` | Full run comparison with failure diffs |
| GET | `/runs/{run_id}/trust-score` | Run trust score |
| GET | `/runs/{run_id}/investigation` | Get LLM investigation result |
| POST | `/runs/{run_id}/investigation` | Trigger LLM investigation |

## Failures

| Method | Path | Description |
|--------|------|-------------|
| GET | `/failures` | List failures with filters (severity, type, search) |
| GET | `/runs/{run_id}/failures` | List failures for a specific run |
| GET | `/failures/{failure_id}` | Single failure with similar failures |
| POST | `/failures/{failure_id}/resolution` | Record a resolution |
| GET | `/failures/{failure_id}/run` | Resolve failure ID to run ID |
| GET | `/failure-atlas` | Search failure atlas entries |
| GET | `/failures/correlation/{failure_type}` | Correlation data for a failure type |

## Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/summary` | Aggregate failure stats (total, fixed, success rate) |
| GET | `/analytics/common-failures` | Most common failure types |
| GET | `/analytics/fix-effectiveness` | Fix success rate by type |
| GET | `/analytics/qor-improvements` | WNS/TNS improvement by fix type |
| GET | `/analytics/failure-trends` | Failure distribution and daily counts |
| GET | `/analytics/resolution-confidence` | Resolution confidence distribution |
| GET | `/analytics/mttr` | Mean-time-to-resolve per failure type |
| GET | `/analytics/coverage` | Atlas coverage analytics |
| POST | `/analytics/event` | Record generic analytics event |
| GET | `/analytics/product` | Product analytics dashboard |

## Regressions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/regressions` | First-detected regression entries per failure type |

## Similar Failures

| Method | Path | Description |
|--------|------|-------------|
| GET | `/similar-failures/{failure_type}` | Fix strategies for a failure type |

## Knowledge Base

| Method | Path | Description |
|--------|------|-------------|
| GET | `/knowledge/failures` | List knowledge base entries |
| GET | `/knowledge/failures/{identifier}` | Lookup failure in KB/signature files |
| GET | `/knowledge/search` | Search knowledge base |
| GET | `/knowledge/qor` | QoR improvement playbook |

## Reliability

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reliability/summary` | Reliability scores and distribution |
| GET | `/reliability/health` | Execution health statuses |
| GET | `/reliability/trends` | Reliability trend report |

## Provenance

| Method | Path | Description |
|--------|------|-------------|
| GET | `/provenance/summary` | Provenance summary (manifests, graph) |
| GET | `/provenance/manifests` | Reproducibility manifests |
| GET | `/provenance/graph` | Provenance graph (nodes + edges) |

## Telemetry

| Method | Path | Description |
|--------|------|-------------|
| GET | `/telemetry/events` | List telemetry events |
| POST | `/telemetry/event` | Record telemetry event |
| GET | `/telemetry/export` | Export sanitized telemetry (json/csv) |
| GET | `/telemetry/health` | Telemetry pipeline health |
| GET | `/telemetry/audit-log` | Telemetry audit log |
| POST | `/telemetry/replay` | Replay telemetry events |
| POST | `/telemetry/snapshot` | Create dataset snapshot |
| GET | `/telemetry/privacy-validate` | Privacy validation report |

## AI Investigation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ai/health` | AI provider availability |
| GET | `/ai/trigger` | Check if AI should trigger for failure params |
| POST | `/ai/investigate` | Generate AI investigation guidance |
| GET | `/ai/investigate/failure` | Investigate a specific failure |
| POST | `/ai/feedback` | Record user feedback on AI guidance |
| GET | `/ai/feedback/{investigation_id}` | Get feedback for an investigation |
| GET | `/ai/feedback-summary` | Aggregated feedback summary |
| POST | `/ai/resolution` | Capture AI-guided resolution |
| GET | `/ai/resolutions` | List captured AI resolutions |

## Resolution Intelligence

| Method | Path | Description |
|--------|------|-------------|
| GET | `/resolutions/patterns` | List resolution patterns |
| GET | `/resolutions/patterns/{fingerprint}/timeline` | Resolution timeline |
| POST | `/resolutions/capture` | Record a fix relationship |
| POST | `/resolutions/feedback` | Record pattern feedback |
| GET | `/resolutions/summary` | Pattern summary statistics |
| GET | `/resolutions/trust-summary` | Trust score distribution |
| GET | `/resolutions/candidates` | Candidates for FA promotion |
| POST | `/resolutions/promote` | Promote candidate to Failure Atlas |
| GET | `/resolutions/top-resolved` | Top resolved failure types |
| GET | `/resolutions/top-unresolved` | Top unresolved failure types |
| GET | `/resolutions/metrics` | Resolution metrics (suggested/accepted/verified) |

## Community Intelligence

| Method | Path | Description |
|--------|------|-------------|
| POST | `/community/escalate` | Create and submit escalation |
| GET | `/community/escalations` | List escalations |
| GET | `/community/escalation/{id}` | Get escalation detail |
| POST | `/community/escalation/{id}/response` | Record engineer response |
| GET | `/community/stats` | Community statistics |
| GET | `/community/unknown-dataset` | Unknown failure dataset (alias) |
| GET | `/community/dataset` | Unknown failure dataset |
| GET | `/community/knowledge-gaps` | Knowledge gap analysis |

## Feedback Center

| Method | Path | Description |
|--------|------|-------------|
| GET | `/feedback` | List feedback records |
| POST | `/feedback` | Submit feedback |
| PATCH | `/feedback/{id}` | Update feedback record |
| GET | `/feedback/stats` | Feedback statistics |
| POST | `/feedback/{id}/prioritize` | Compute priority score |

## Support Bundle

| Method | Path | Description |
|--------|------|-------------|
| POST | `/support-bundle/generate` | Generate support bundle ZIP |

## User Journey

| Method | Path | Description |
|--------|------|-------------|
| POST | `/journey/event` | Record user journey event |
| GET | `/journey` | Get journey events |
| GET | `/journey/report` | Funnel analysis report |

## Atlas Metrics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/atlas/trust-summary` | Failure Atlas trust summary |
| GET | `/atlas/metrics` | Atlas coverage metrics |

## Beta

| Method | Path | Description |
|--------|------|-------------|
| GET | `/beta/dashboard` | Comprehensive beta dashboard |
| GET | `/beta/report` | Weekly beta report |

## Generic

| Method | Path | Description |
|--------|------|-------------|
| POST | `/record-event` | Record generic event |

## Static Files

The dashboard SPA is mounted at `/` when `dashboard/dist` exists, serving all unhandled paths as `index.html`.
