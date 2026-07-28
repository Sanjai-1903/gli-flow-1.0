# Long Run UX Design

## Problem

During ORFS execution, the user sees only the stage name:

```
ORFS: PACKAGING
```

The picorv32 run spent ~38 minutes inside PACKAGING (which includes synthesis,
floorplanning, placement, CTS, routing, and fill). The user cannot distinguish
"working" from "stuck" because:
- No elapsed time shown
- No sub-stage visibility
- No routing iteration/violation trend
- No estimated remaining time

## Solution: Live Progress Dashboard

### New display format:

```
ORFS: Detailed Routing
  Elapsed: 12m 34s | Stage: 5/12 | Violations: 8712 → 5106 → 4781 → 0
  ████████████░░░░░░░░  62%
```

### Data collected by `OrfsMonitor`:

| Field | Source | Example |
|-------|--------|---------|
| Current ORFS stage | Makefile output parsing | `5_2_route` |
| Human-readable label | Stage label mapping | "Detailed Routing" |
| Elapsed time | Wall clock | 754 seconds |
| Sub-stage count | Stage label mapping | 5/12 |
| Routing completion % | `5_2_route.tmp.log` parsing | 62% |
| Routing violations | Violation count parsing | 4781 |
| Violation trend | Previous poll values | 8712→5106→4781→0 |
| Last activity timestamp | Last line written to log | 30s ago |

### Display in CLI (`OrfsStageProgress` → `progress_callback`):

```
ORFS: <human_label>
  Elapsed: <mm:ss> | Stage: <current>/<total> 
  <progress_bar> <pct>%
  Violations: <trend>
  Last activity: <seconds>s ago
```

### Display in Dashboard:

New `/live_runs` endpoint returns:
```json
{
  "run_id": "...",
  "stage": "ROUTING",
  "orfs_stage": "5_2_route",
  "orfs_label": "Detailed Routing",
  "elapsed_seconds": 754,
  "stage_total": 12,
  "stage_current": 5,
  "routing_iteration_pct": 62,
  "routing_violations": 4781,
  "violation_trend": [8712, 5106, 4781],
  "last_activity_seconds_ago": 30,
  "estimated_remaining": "~8 minutes"
}
```

### Implementation changes:

1. `orfs_monitor.py`: Add elapsed time tracking, violation trend buffer, 
   stage progress counter, last activity timestamp
2. `orchestrator.py`: Pass enhanced progress data through callback chain
3. `cli/main.py`: Enhanced progress display in `run_command()`
4. `backend/server.py`: Enhanced `/live_runs` endpoint
5. `dashboard/src/RunMonitorPage.jsx`: Enhanced live view
