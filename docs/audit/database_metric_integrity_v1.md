# Database Metric Integrity v1

## Source
Database: `/home/gli/.gli_flow/gli_flow.db`
Backend uses this path via `_get_db_path()` in `migrations.py:486-501`.

## Values for Latest Runs

| Design (run_id) | wns | tns | hold_wns | hold_tns | qor_score | signoff_score | impl_score | signoff_status | tapeout_ready |
|---|---|---|---|---|---|---|---|---|---|
| counter (`...8869499f_counter`) | 0.05 | 0.0 | NULL | NULL | 0.6 | 1.0 | 0.6 | PASS | 1 |
| gcd (`...62c195de_gcd`) | 0.0 | 0.0 | NULL | NULL | 0.74 | 1.0 | 0.74 | PASS | 1 |
| uart_top (`...fa6710f6_uart_top`) | 0.0 | 0.0 | NULL | NULL | 0.57 | 1.0 | 0.57 | PASS | 1 |
| picorv32 (`...aca911db_picorv32`) | 0.0 | 0.0 | NULL | NULL | **0.0** | **1.0** | **0.0** | PASS | 1 |

## Ground Truth Comparison

### WNS (Dashboard & Database vs Report)

| Design | Report WNS | Database WNS | Match? |
|--------|-----------|--------------|--------|
| counter | 0.05 | 0.05 | ✅ |
| gcd | 0.0 | 0.0 | ✅ |
| uart_top | 0.0 | 0.0 | ✅ |
| picorv32 | 0.0 | 0.0 | ✅ |

### TNS (Dashboard & Database vs Report)

| Design | Report TNS | Database TNS | Match? |
|--------|-----------|--------------|--------|
| counter | 0.00 | 0.0 | ✅ |
| gcd | 0.0 | 0.0 | ✅ |
| uart_top | 0.0 | 0.0 | ✅ |
| picorv32 | 0.0 | 0.0 | ✅ |

### QoR Score (Dashboard & Database vs Calculated)

| Design | QoR Inputs | Expected QoR | Database QoR | Match? |
|--------|-----------|--------------|--------------|--------|
| counter | t=1.0, a=0.58, d=1.0, r=42s | 0.60 | 0.6 | ✅ |
| gcd | t=1.0, a=0.96, d=1.0, r=51.8s | 0.74 | 0.74 | ✅ |
| uart_top | t=1.0, a=0.82, d=1.0, r=63.6s | 0.57 | 0.57 | ✅ |
| picorv32 | t=1.0, a=0.87, d=1.0, r=1107s | **~0.96** | **0.0** | ❌ |

## Discrepancies Found

### Issue A: hold_wns NULL for all designs
All four latest runs have `hold_wns = NULL` in the database. The parser expects `metrics.csv` to have a `hold_whs` column or `timing.rpt` to exist — neither is present in newer runs.

**Impact**: Low for current QoR (fallback to `_corner_results` works in `_compute_qor()`). High if `_compute_qor()` were called without corner_results.

### Issue B: QoR Score = 0.0 for picorv32
The database stores `qor_score = 0.0` for picorv32 even though:
- Timing is fully met (wns=0.0, tns=0.0)
- QoR breakdown shows timing=1.0, area=0.87, density=1.0
- Signoff score = 1.0, tapeout_ready = true

**Root cause**: See timing_qor_integrity_certification_v1.md

### Issue C: setup_wns_ns and signoff timing fields NULL/False
For picorv32: `setup_wns_ns = NULL`, `signoff_setup_pass = 0`, `signoff_hold_pass = 0`, but `signoff_status = PASS` and `tapeout_ready = 1`.

These come from `update_run_signoff()` vs `update_run()` which are called at different points. The signoff timing fields are not updated consistently.
