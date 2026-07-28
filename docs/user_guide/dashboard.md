# Dashboard Guide

## Launch

```bash
gli-flow dashboard                # Backend + frontend dev server
gli-flow dashboard --backend-only # API only at http://127.0.0.1:8000
```

The full dashboard opens at `http://127.0.0.1:5173`. The backend-only mode serves the API.

## Pages

### Home

**Dashboard** — landing page with:
- Metric cards (total runs, pass/fail count, average QoR)
- QoR trend chart over recent runs
- Recent runs table (run ID, design name, status, QoR, failures, runtime)
- Infrastructure health status

### Execution

| Page | Description |
|------|-------------|
| **Run Design** | CLI command reference for running designs |
| **Run Matrix** | Design × Stage grid showing execution progress per stage |
| **Run Monitor** | Live run monitor with recent activity feed |
| **Important Runs** | Filtered view of starred/bookmarked runs |
| **Artifacts** | Browse run artifacts with in-browser preview |

### Run Detail

Click any run to open its detail page with 10 tabs:

1. **Summary** — run metadata, trust score, QoR, WNS, TNS, tapeout readiness
2. **Timing** — multi-corner STA results (setup WNS, setup TNS per corner)
3. **Area & Power** — utilization %, cell count, die area, power breakdown (internal, switching, leakage)
4. **DRC/LVS** — DRC violations table, LVS result (PASS/FAIL)
5. **Layout Images** — 5 views: final_all, final_placement, final_routing, final_clocks, final_ir_drop
6. **Artifacts** — full artifact viewer supporting text, image, PDF, HTML
7. **Failure Atlas** — per-run failure detections with severity and resolution linking
8. **Reproducibility** — reproducibility manifest (tool versions, PDK, timestamps)
9. **AI Investigation** — LLM-powered root cause analysis (if AI provider configured)
10. **Compare** — side-by-side run comparison with regression detection

### Intelligence

| Page | Description |
|------|-------------|
| **QoR Analytics** | QoR score trends over time |
| **Regression Detector** | Run-to-run regression comparison |
| **Trends & Reports** | Timeline view, top runs, trends |
| **Failure Atlas** | Full atlas with search, filters, analytics, feedback |
| **Engineering Dashboard** | Community escalations, resolution statistics |

### Governance

| Page | Description |
|------|-------------|
| **Provenance** | Design provenance and metadata |
| **Release Validation** | Release validation status |
| **Policy Suite** | Policy configuration |

### Beta

| Page | Description |
|------|-------------|
| **Beta Dashboard** | Beta program operations and metrics |
| **Feedback Center** | Submit and track feedback |
| **Product Analytics** | Product usage analytics |
| **User Journey** | User journey tracking |

### System

| Page | Description |
|------|-------------|
| **Infrastructure** | API health, tool versions, system status |
| **Telemetry** | Transparency center: events, unknown failures, escalations, resolution patterns, upload preview |
| **Telemetry Health** | Pipeline health metrics and connectivity status |
| **Telemetry Replay** | Replay/dry-run telemetry uploads |
| **Help** | Help and documentation |
| **Settings** | App config, AI provider setup |

## API

The backend serves a REST API at `http://127.0.0.1:8000/api/`. Key endpoints:

- `GET /api/runs` — list runs
- `GET /api/runs/<id>` — run details
- `GET /api/designs` — list designs
- `GET /api/health` — infrastructure health

The frontend dev server proxies `/api/*` to the backend.

## Common Tasks

**View run results:** Dashboard → click run ID → Summary tab  
**Check DRC violations:** Dashboard → click run ID → DRC/LVS tab  
**Compare two runs:** Dashboard → click run ID → Compare tab  
**View Failure Atlas:** Dashboard → Failure Atlas page → search/filter  
**Monitor live runs:** Dashboard → Run Monitor page
