# GLI-FLOW Failure Atlas

This directory documents known EDA failure modes, their root causes, detection patterns, and verified fixes. When a run fails, GLI-FLOW cross-references these entries to provide actionable error messages.

## Index

| FA-ID | Category | Failure Mode | Detection Stage |
|-------|----------|-------------|-----------------|
| FA-0001 | SYNTHESIS | Latch inference | Synthesis |
| FA-0002 | ROUTING | Global routing overflow | Routing / PACKAGING |
| FA-0003 | SYNTHESIS | Multi-driver nets | Synthesis |
| FA-0004 | SYNTHESIS | Missing module (blackboxed) | Synthesis |
| FA-0005 | DRC/LVS | DRC violations | DRC |
| FA-0006 | TIMING | Hold timing violations | STA / TIMING_ANALYSIS |
| FA-0007 | OOM | Out-of-memory (SIGKILL) | Any stage |
| FA-0008 | TIMEOUT | Stage timeout | Any stage |
| FA-0009 | TOOL | Tool not found / broken | Environment validation |
| FA-0010 | PDK | PDK missing or misconfigured | Environment validation |
| FA-0011 | RTL | SystemVerilog unsupported constructs | Synthesis |
| FA-0012 | ROUTING | Antenna violations | Post-route |
| FA-0013 | TIMING | Max transition violations | STA |
| FA-0014 | TIMING | Max capacitance violations | STA |
| FA-0015 | DENSITY | Metal density out of range | DRC / DENSITY_CHECK |
| FA-0016 | MACRO | SRAM macro missing liberty file | Pre-synthesis |
| FA-0017 | CDC | Clock domain crossing (untested) | CDC check |
| FA-0018 | PATH | Path length too long | Manifest validation |
| FA-0019 | SYNTHESIS | Latch inference (detailed) | Synthesis log |
| FA-0020 | LOCALE | Locale decimal separator corruption | All subprocess |
| INF-PWR-001 | POWER | Power signoff unconditional pass | Signoff |

## FA-0001: Latch Inference

**Detection:** Synthesis tool outputs "Latch inferred for signal X"
**Root Cause:** Incomplete if/case statements without default assignments
**Severity:** TAPEOUT_BLOCKING
**Fix:** Add default assignment in every if/case branch. Use always_ff for intended registers.
**Reference:** Yosys docs: https://yosyshq.readthedocs.io/en/latest/yosys_manual.html

## FA-0002: Global Routing Overflow

**Detection:** OpenROAD GRT reports "Horizontal overflow: N%" or "Vertical overflow: N%"
**Root Cause:** Floorplan core utilization too high for the design
**Severity:** TAPEOUT_BLOCKING (above 5%)
**Fix:** Reduce FP_CORE_UTIL by at least 15% in gli_manifest.yaml
**Reference:** OpenROAD GRT documentation: https://openroad.readthedocs.io/

## FA-0003: Multi-Driver Nets

**Detection:** Yosys reports "multiple drivers on net X"
**Root Cause:** Two or more always blocks or assign statements driving the same net
**Severity:** TAPEOUT_BLOCKING
**Fix:** Each net must have exactly one driver. Use a mux or priority encoder.
**Reference:** Verilog standard IEEE 1364-2005 Section 5.6

## FA-0004: Missing Module (Blackboxed)

**Detection:** Yosys reports "Module X not found" and blackboxes it
**Root Cause:** RTL references a module whose source file is not in rtl_files
**Severity:** TAPEOUT_BLOCKING
**Fix:** Add the missing module's source file to rtl_files in gli_manifest.yaml
**Reference:** Yosys `hierarchy -check` command

## FA-0005: DRC Violations

**Detection:** Magic or KLayout reports DRC violations
**Root Cause:** Layout violates foundry manufacturing design rules
**Severity:** TAPEOUT_BLOCKING
**Fix:** Review DRC report, adjust floorplan or routing
**Reference:** PDK DRC rule deck documentation

## FA-0006: Hold Timing Violations

**Detection:** STA reports hold WNS < 0
**Root Cause:** Flip-flop hold time not met; data arrives too early relative to clock
**Severity:** TAPEOUT_BLOCKING
**Fix:** Add `set_fix_hold` to SDC constraints. Increase hold margin.
**Reference:** OpenSTA hold fixing: https://github.com/The-OpenROAD-Project/OpenSTA

## FA-0007: Out of Memory (OOM)

**Detection:** Process killed with signal -9 (SIGKILL) or "Killed" in stderr
**Root Cause:** Design too large for available RAM
**Severity:** CRITICAL
**Fix:** Reduce design complexity, increase RAM, or use --memory flag
**Reference:** Linux OOM killer documentation

## FA-0008: Stage Timeout

**Detection:** Stage exceeds configured timeout
**Root Cause:** Design too complex or infinite loop in EDA tool
**Severity:** CRITICAL
**Fix:** Increase timeout with --timeout flag or reduce design complexity

## FA-0009: Tool Not Found

**Detection:** Tool binary not found in PATH
**Root Cause:** EDA tool not installed
**Severity:** CRITICAL
**Fix:** Run `gli-flow install` to install missing tool

## FA-0010: PDK Misconfiguration

**Detection:** PDK_ROOT not set or PDK not found
**Root Cause:** PDK not installed or PDK_ROOT environment variable not set
**Severity:** CRITICAL
**Fix:** Set PDK_ROOT environment variable or run `gli-flow install --pdk sky130`

## FA-0011: SystemVerilog Unsupported Constructs

**Detection:** sv2v fails or Yosys produces wrong netlist
**Root Cause:** Verilog file contains SystemVerilog constructs not supported by sv2v
**Severity:** BLOCKING
**Fix:** Use Verilog-2001 compatible syntax. Avoid SV-specific constructs.
**Reference:** sv2v documentation: https://github.com/zachjs/sv2v

## FA-0012: Antenna Violations

**Detection:** OpenROAD reports antenna violations
**Root Cause:** Long metal wires charge during plasma etching, damaging transistor gates
**Severity:** TAPEOUT_BLOCKING
**Fix:** Automatic diode insertion via OpenROAD's antenna repair
**Reference:** OpenROAD antenna checker documentation

## FA-0013: Max Transition Violations

**Detection:** STA reports max transition violations
**Root Cause:** Signal slew rate too slow due to high fanout or long wire
**Severity:** WARNING (can cause timing failures)
**Fix:** Add buffer trees, reduce fanout, or upsize drivers

## FA-0014: Max Capacitance Violations

**Detection:** STA reports max capacitance violations
**Root Cause:** Net capacitance exceeds library maximum
**Severity:** WARNING (can cause timing failures)
**Fix:** Split high-fanout nets, add buffers

## FA-0015: Metal Density Out of Range

**Detection:** DRC reports density violations on specific metal layers
**Root Cause:** Metal density too low or too high per PDK rules
**Severity:** TAPEOUT_BLOCKING
**Fix:** Add dummy fill or adjust routing density
**Reference:** PDK density rule documentation

## FA-0016: SRAM Macro Missing Liberty File

**Detection:** SRAM macro in manifest has no liberty_file
**Root Cause:** Behavioral SRAM model has no timing constraints
**Severity:** WARNING
**Fix:** Add liberty_file to macro definition in gli_manifest.yaml

## FA-0017: Clock Domain Crossing (CDC) Untested

**Detection:** Multiple clock domains detected
**Root Cause:** Design has multiple clock domains but no CDC analysis was run
**Severity:** MANDATORY DISCLAIMER
**Fix:** Use dedicated CDC tool (SpyGlass CDC, Questa CDC, sv-cdc)
**Reference:** GLI-FLOW v1.0 does not perform CDC analysis

## FA-0018: Path Length Too Long

**Detection:** Design directory path too long (>180 chars)
**Root Cause:** Deeply nested directory structure
**Severity:** BLOCKING
**Fix:** Move design closer to filesystem root

## FA-0019: Latch Inference (Detailed)

**Detection:** Yosys reports latch inference during synthesis
**Root Cause:** Incomplete case statements, missing default assignments
**Severity:** TAPEOUT_BLOCKING
**Fix Patterns:**
```verilog
// BAD - latch inferred
always @(*) begin
    if (sel) out = a;
    // missing else
end

// GOOD - no latch
always @(*) begin
    if (sel) out = a;
    else out = b;
end

// BETTER - use always_ff for registers
always_ff @(posedge clk) begin
    if (sel) out <= a;
end
```

## INF-PWR-001: Power Signoff Unconditional Pass

**Detection:** Power signoff passes even when power analysis was never run, crashed, or produced all-zero results.

**Root Cause:** `orchestrator.py` stage dispatcher unconditionally set `self.signoff_gate.power_pass = True` at line ~984 after POWER stage completion, regardless of whether `_run_power_analysis()` actually succeeded. The exception handler in `_run_power_analysis()` returns a zeroed `PowerResult`, which then flows through the unconditional pass assignment. The dashboard then shows "PASS" for power signoff with "—" (no data) for all power metrics.

**Original Code (vulnerable):**
```python
if stage == "POWER":
    self.signoff_gate.power_pass = True  # always True after POWER stage
```

**Detection Pattern:** Telemetry reports power metrics as `None`/`0.0` but signoff gate shows `power_pass=True`. Dashboard displays "PASS" with empty metrics.

**Severity:** CRITICAL (silent data corruption, undetected power delivery failures)

**Fix:** Replace unconditional assignment with multi-condition check:
1. Power report file must exist on disk
2. Parser must have successfully extracted `total_power_mw > 0`
3. IR violation limits must be respected

```python
if stage == "POWER":
    power_result = ...  # actual parser result
    if power_result and power_result.total_power_mw > 0:
        self.signoff_gate.set_power_pass(True)
    else:
        self.signoff_gate.set_power_pass(False, failure_reason="...")
```

**Verification:** Run `test_power_signoff_integrity` regression. Confirm that a POWER stage producing zeroed results yields `power_pass=False` and a Failure Atlas entry is logged.

**Reference:** `gli_flow/core/orchestrator.py` line ~984, `tests/test_not_run_hardening.py`

## FA-0020: Locale Decimal Separator Corruption

**Detection:** WNS appears unrealistically good (87x better than actual)
**Root Cause:** Non-English locale uses "," as decimal separator; parser reads "1,28" as "1"
**Severity:** SILENT DATA CORRUPTION
**Fix:** All subprocess calls now use LC_ALL=C via safe_env()
**Verification:** grep -rn "subprocess.run\|subprocess.Popen" gli_flow/ --include="*.py" | grep -v "safe_env\|LC_ALL" should return zero results
