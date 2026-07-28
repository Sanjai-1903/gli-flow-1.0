# Root Cause Engine Design

## Problem

Current Failure Atlas entries are symptom-level:
```
DRC failed
Magic DRC failed
Signoff failed
LVS failed
Pipeline failed
```

These are consequences, not root causes. A user cannot determine:
- What actually failed
- Why it failed
- Whether RTL is bad, flow is bad, or tool is bad
- What action to take next

## Solution: Root Cause Hierarchy

```
ROOT CAUSE
├── Evidence (multiple sources)
├── Consequences (symptoms caused by this root cause)
└── Recommendations (actionable steps)
```

### Root Cause Types

| Type | Description | Example |
|------|-------------|---------|
| `DESIGN_TIMING_VIOLATION` | Design does not meet timing constraints | Setup WNS = -0.5ns |
| `DESIGN_DRC_VIOLATION` | Physical design has rule violations | 6 DRC violations (li.3) |
| `FLOW_EXTRACTION_TIMEOUT` | Tool extraction exceeded limit | LVS extraction > 600s |
| `FLOW_CONFIG_ERROR` | Flow configuration is incorrect | Missing PDK path |
| `TOOL_FALSE_POSITIVE` | Tool reports invalid violations | Magic licon.8a (INF-MAGIC-002) |
| `ENVIRONMENT_MISMATCH` | Environment missing requirements | Missing DISPLAY for Magic |
| `DESIGN_OVERSIZE` | Design too large for current flow | Extraction OOM |

### Data Model

```python
@dataclass
class RootCause:
    root_cause_id: str
    run_id: str
    root_cause_type: str          # One of ROOT_CAUSE_TYPES
    severity: str                 # TAPEOUT_BLOCKING, PERFORMANCE, INFO
    summary: str                  # One-line human-readable
    detail: str                   # Multi-line with evidence
    confidence: float             # 0.0 - 1.0
    evidence: dict                # {file: [line_numbers]}
    consequences: list[str]       # Symptom entries caused by this
    recommendations: list[str]    # Ordered actionable steps
    design_name: str
    detected_at: str
```

### Detection Algorithm

```
For each failed run:
  1. Collect all evidence files (magic_drc.rpt, klayout_drc.xml, 
     drc_lvs_summary.json, error.log, openroad.log, timing reports)
  
  2. Analyze each domain:
     a. DRC: Parse magic_drc.rpt for violations, klayout_drc.xml for 
        cross-tool comparison. Identify real violations vs false positives.
     b. LVS: Parse drc_lvs_summary.json for timeout, unmatched, errors.
     c. Timing: Parse signoff reports for WNS/TNS.
     d. Pipeline: Parse error.log for stage failures.
     e. Environment: Check for known tool issues (DISPLAY, PATH).
  
  3. Group symptoms to root causes:
     - licon.8a + KLayout silence → TOOL_FALSE_POSITIVE (INF-MAGIC-002)
     - li.3 violations (both tools agree) → DESIGN_DRC_VIOLATION
     - LVS timeout + large .ext → FLOW_EXTRACTION_TIMEOUT
     - Setup WNS < 0 → DESIGN_TIMING_VIOLATION
  
  4. Identify PRIMARY blocker:
     - The root cause that must be resolved first
     - Usually the one earliest in the flow
     - Blocks all downstream signoff checks
  
  5. Generate recommendations:
     - Reference specific reports and line numbers
     - Ordered by: quickest fix first, then most impactful
```

### Implementation

The engine is at `gli_flow/reliability/root_cause_engine.py` with:

- `RootCause` dataclass
- `RootCauseEngine.analyze(run_dir, design_name, signoff_gate) -> RootCauseReport`
- `RootCauseReport` containing multiple `RootCause` objects, primary blocker, summary

The engine is called from `orchestrator.py` after failure detection and before 
Failure Atlas recording. The root causes are stored in a new `root_causes` 
table in the database.
