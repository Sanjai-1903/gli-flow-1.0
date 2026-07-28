# RISC-V Onboarding Gap Analysis

## Critical Gaps

### G1: ORFS_ROOT Configuration Ambiguity
- **Issue:** `ORFS_ROOT` can point to either the ORFS root (`.../orfs`) or the flow directory (`.../orfs/flow`). The config.yaml default `orfs_root: /home/bolter/.gli-flow/orfs` caused the environment validator to construct `orfs_root/flow/flow` when the value was set to the flow directory.
- **Impact:** New users will hit this on first real run. Error message is confusing.
- **Fix:** Standardize on one convention. Document clearly. Validate during install.

### G2: Missing PDK_ROOT/ORFS_ROOT in Default Config
- **Issue:** `install` sets these in `config.yaml` but they are not automatically exported as environment variables. `run` uses `os.environ.setdefault("PDK_ROOT", ...)` but `ORFS_ROOT` is read inconsistently.
- **Impact:** Users need to manually export variables or edit config.yaml.
- **Fix:** Ensure `run` command sets both PDK_ROOT and ORFS_ROOT from config if not in environment.

### G3: sv2v Preprocessing Catch-22
- **Issue:** Many real Verilog designs use `always @*` and `integer` loops which trigger sv2v detection. sv2v may introduce subtle differences.
- **Impact:** Unexpected preprocessing can break known-good RTL.
- **Fix:** Add `skip_sv2v: true` manifest option. Document which constructs trigger sv2v.

## Major Gaps

### M1: Real Run Takes >30x Counter Example
- **Issue:** Counter: <1 min. PicoRV32: ~39 min. No runtime estimation provided.
- **Documentation:** No guidance on expected runtime vs design complexity.
- **Fix:** Add design-size-based runtime estimation to `gli-flow run` output.

### M2: STA Parser Extracts Wrong Values
- **Issue:** Real ORFS timing (WNS=12.83 ns) not extracted. Parser shows WNS=0.0, hold_wns=Infinity.
- **Impact:** Signoff timing appears wrong. QoR score is 0.0 despite great timing.
- **Fix:** Update telemetry parser to read `6_report.json` format from ORFS.

### M3: LVS Timeout Hardcoded at 600s
- **Issue:** Netgen LVS extraction timed out after 600 seconds for a CPU-sized design.
- **Impact:** LVS never completes for designs >5000 cells.
- **Fix:** Make LVS timeout configurable in manifest. Add progress indication.

### M4: No Warning About Real Run Duration
- **Issue:** No indication that PACKAGING will take 30-60 minutes.
- **Impact:** Users think the tool is stuck/hung.
- **Fix:** Print "Estimated runtime: ~X minutes" before PACKAGING stage.

## Minor Gaps

### m1: CDC Warning Unclear for Single-Clock Design
- **Issue:** PicoRV32 is single-clock but CDC detection reports "2 clock domain(s)."
- **Root Cause:** Async reset (`negedge resetn`) counted as separate clock domain.
- **Fix:** Filter async reset edges from CDC detection or add clarification to warning.

### m2: DRC Report Format Not Human-Readable
- **Issue:** Magic DRC report is a single-line JSON-like dump, not formatted.
- **Fix:** Format DRC report with proper line breaks and coordinate descriptions.

### m3: Missing Die Photo/Layout Image
- **Issue:** Placeholder images generated instead of actual GDS screenshots.
- **Fix:** Auto-generate layout PNG from GDS using KLayout.

### m4: `finish__flow__errors__count: 1` Not Explained
- **Issue:** ORFS report shows 1 error but no details on what it was.
- **Fix:** Investigate ORFS error and either fix or document in known limitations.

## Gap Priority Summary

| ID | Gap | Severity | Impact |
|----|-----|----------|--------|
| G1 | ORFS_ROOT ambiguity | Critical | Blocks first real run |
| G2 | Missing env vars | Critical | Blocks first real run |
| G3 | sv2v preprocessing | Critical | Can break RTL |
| M1 | No runtime estimation | Major | Bad UX |
| M2 | STA parser fails | Major | Wrong metrics |
| M3 | LVS timeout | Major | Blocking for CPU designs |
| M4 | No duration warning | Major | Bad UX |
| m1 | CDC false positive | Minor | Confusing warning |
| m2 | DRC format | Minor | Hard to debug |
| m3 | No GDS image | Minor | Less visual feedback |
| m4 | ORFS error unexplained | Minor | Hard to debug |
