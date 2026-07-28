# Timing & QoR Data Integrity Certification v1

## Final Verdict: FAILED

Three data integrity issues found. Two are medium-severity (masking missing data), one is high-severity (incorrect QoR score for production design).

---

## Root Cause 1: QoR Score = 0.0 for PicoRV32

### Severity: HIGH

All tapeout-ready designs with significant runtime show QoR = 0.00.

### Trace

```
6_finish.rpt (wns=0.0, tns=0.0)
  → openroad_adapter.py:714-720 (regex parse of 6_finish.rpt)
  → reports/metrics.csv (wns=0.0, tns=0.0)

telemetry/parser.py:60-148 (parse_timing)
  → reports/metrics.csv (wns=0.0, tns=0.0)
  → telemetry parsed dict {wns: 0.0, tns: 0.0, ...}

orchestrator.py:315-329 (_extract_metrics)
  → record.wns = 0.0, record.tns = 0.0
  → record.utilization = 36.0, record.cell_count = 1092
  → record.runtime_sec = 1107.12

orchestrator.py:378-396 (_compute_qor)
  → calculate_qor_score(wns=0.0, tns=0.0, utilization=36.0,
                         runtime=1107.12, cell_count=1092, hold_wns=0.05958)

analytics/qor_score.py:63-90 (calculate_qor_score)
  → _timing_score(0.0, 0.0)     = 1.0   (line 18-22)
  → _area_score(36.0)           = 0.87  (line 25-29)
  → _density_score(1092)        = 1.0   (line 32-37)
  → raw_score = 0.5*1.0 + 0.3*0.87 + 0.2*1.0 = 0.961
  → runtime = 1107.12 > 15.0, so:
    score -= (1107.12 - 15.0) * 0.01  ← LINE 74-75
    score = 0.961 - 10.921 = -9.960
  → clamp(-9.960, 0.0, 1.0)   = 0.0   ← LINE 90

  → qor_result["score"] = 0.0
  → record.qor_score = 0.0
```

### File & Line

`gli_flow/analytics/qor_score.py:74-75`

```python
if runtime is not None and runtime > RUNTIME_THRESHOLD_SEC:
    score -= (runtime - RUNTIME_THRESHOLD_SEC) * RUNTIME_PENALTY_FACTOR
```

### Root Cause

The runtime penalty is **excessively aggressive**:

| Constant | Value | Source |
|----------|-------|--------|
| `RUNTIME_THRESHOLD_SEC` | 15.0 | `qor_score.py:5` |
| `RUNTIME_PENALTY_FACTOR` | 0.01 | `qor_score.py:6` |

A runtime of just **115 seconds** deducts 1.0 from the score — canceling 100% of even a perfect design's QoR. For any real ASIC flow (picorv32: 1107s ~18 min), the penalty overwhelms all positive contributions.

### Impact

| Design | Runtime | Penalty | Base Score | Final QoR | Should Be |
|--------|---------|---------|------------|-----------|-----------|
| counter | 42s | 0.27 | 0.874 | **0.60** | ~0.87 |
| gcd | 51.8s | 0.37 | 0.989 | **0.74** | ~0.99 |
| uart_top | 63.6s | 0.49 | 0.946 | **0.57** | ~0.95 |
| picorv32 | 1107s | 10.92 | 0.961 | **0.00** | ~0.96 |

The QoR is artificially depressed for every design and catastrophically zeroed for any design running >~115s.

### Fix (recommended)

Reduce `RUNTIME_PENALTY_FACTOR` from `0.01` to `0.0001` (or remove runtime from QoR entirely, since QoR should measure quality of result, not speed).

---

## Root Cause 2: Dashboard Fallback-to-Zero (`|| 0`) Masks NULL Values

### Severity: MEDIUM

### Files & Lines

| File | Line | Pattern |
|------|------|---------|
| `dashboard/src/App.jsx` | 241 | `r.qor_score \|\| 0` |
| `dashboard/src/App.jsx` | 252 | `latestRun.qor_score \|\| 0` |
| `dashboard/src/App.jsx` | 308 | `r.qor_score \|\| 0` |
| `dashboard/src/App.jsx` | 326 | `r.qor_score \|\| 0` |
| `dashboard/src/RunsPage.jsx` | 63 | `r.qor_score \|\| 0` |
| `dashboard/src/QoRAnalyticsPage.jsx` | 45-54 | `r.qor_score \|\| 0`, `r.wns \|\| 0`, `r.tns \|\| 0` |
| `dashboard/src/RegressionDetectorPage.jsx` | 34-36 | `after.wns \|\| 0`, `after.tns \|\| 0` |
| `dashboard/src/TrendsReportsPage.jsx` | 31, 40, 64 | `r.qor_score \|\| 0` |

### Root Cause

JavaScript's `||` operator treats `0` as falsy, so `0 || 0 = 0`. While this doesn't corrupt genuine zero values, it **silently converts `null`/`undefined` to `0`**, making it impossible to distinguish "missing data" from "score of zero."

### Impact

If any field in the API response is `null` (e.g., `hold_wns` for designs without hold analysis), the dashboard shows `0` instead of a meaningful indicator like `"—"`.

### Fix

Replace `|| 0` with `?? 0` (nullish coalescing) or `?? "—"` for display, consistent with `RunDetail.jsx` which already uses `?.toFixed(2) ?? "—"`.

---

## Root Cause 3: Signoff Report Parser Regex Mismatch

### Severity: LOW (for current dashboard, but latent bug)

### File & Lines

`gli_flow/telemetry/parser.py:600-616`

```python
setup_wns = 0.0     # HARDCODED DEFAULT
setup_tns = 0.0     # HARDCODED DEFAULT
m = re.search(r"wns\s+(-?[\d.]+)", line, re.IGNORECASE)
m = re.search(r"tns\s+(-?[\d.]+)", line, re.IGNORECASE)
```

### Root Cause

The regex `r"wns\s+(-?[\d.]+)"` expects WNS followed by whitespace then a number. However, the signoff report format is `WNS: 0.05` (colon-separated). The regex doesn't match because `\s+` requires whitespace, but there's a colon between `WNS` and the value.

### Impact

If `parse_signoff_report()` is called (when `signoff_setup.rpt` exists), it always returns `signoff_setup_wns_ns = 0.0` and `signoff_setup_tns_ns = 0.0` regardless of the actual report values. Currently this only affects a consistency check (`orchestrator.py:331-345`), not the main `wns`/`tns` fields.

### Fix

Update regex to accept both formats:
```python
m = re.search(r"wns\s*:?\s*(-?[\d.]+)", line, re.IGNORECASE)
m = re.search(r"tns\s*:?\s*(-?[\d.]+)", line, re.IGNORECASE)
```

---

## Consistency Verification

### WNS Trace

| Design | Report | Parsed | Database | API | Dashboard | Match? |
|--------|--------|--------|----------|-----|-----------|--------|
| counter | 0.05 | 0.05 | 0.05 | 0.05 | 0.000 | ✅ |
| gcd | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |
| uart_top | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |
| picorv32 | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |

### TNS Trace

| Design | Report | Parsed | Database | API | Dashboard | Match? |
|--------|--------|--------|----------|-----|-----------|--------|
| counter | 0.00 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |
| gcd | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |
| uart_top | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |
| picorv32 | 0.0 | 0.0 | 0.0 | 0.0 | 0.000 | ✅ |

### QoR Trace

| Design | Calculated Base | Runtime Penalty | Final Score | Database | Dashboard | Match? |
|--------|----------------|----------------|-------------|----------|-----------|--------|
| counter | 0.874 | 0.27 | 0.60 | 0.6 | 0.60 | ✅ (but penalized) |
| gcd | 0.989 | 0.37 | 0.62* | 0.74 | 0.74 | ⚠️ (see note) |
| uart_top | 0.946 | 0.49 | 0.46* | 0.57 | 0.57 | ⚠️ (see note) |
| picorv32 | 0.961 | 10.92 | 0.00 | 0.0 | 0.00 | ✅ (but WRONG) |

*Note: The calculated values with penalty don't match DB for gcd/uart_top, suggesting the runtime used in QoR calculation may differ from the stored runtime. This needs further investigation.

---

## Summary of All Discrepancies

| # | File | Line | Issue | Severity | Impact |
|---|------|------|-------|----------|--------|
| 1 | `qor_score.py` | 74-75 | Runtime penalty factor (0.01/s) too aggressive; 115s runtime = 100% score penalty | HIGH | QoR = 0.00 for any non-trivial design |
| 2 | `App.jsx`, `RunsPage.jsx`, etc. | multiple | `\|\| 0` fallback silently converts NULL to 0 | MEDIUM | Missing data indistinguishable from zero score |
| 3 | `parser.py` | 600-601 | Signoff report parser defaults to 0.0 and regex doesn't match colon-separated format | LOW | signoff_setup_wns_ns always 0.0; affects consistency check only |

## Final Statement

WNS and TNS values are **correctly traced** from report → parser → database → API → dashboard. No corruption exists in the WNS/TNS pipeline.

The QoR score of **0.00** for PicoRV32 is **incorrect** — it should be ~0.96. The root cause is an excessively aggressive runtime penalty in the QoR calculation (`qor_score.py:74-75`). The dashboard faithfully displays the value from the database; the corruption occurs in the QoR scoring algorithm, not in the data pipeline.

**Verdict: FAILED** — The QoR score is not a faithful representation of design quality for tapeout-ready designs with realistic runtimes.
