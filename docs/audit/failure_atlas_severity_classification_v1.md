# Failure Atlas Severity Classification v1

**Date:** 2026-06-20
**Purpose:** Classify every existing Failure Atlas entry type into the new 5-tier severity model

---

## Classification Table

| Category (FailureCategory enum) | Description | Current Severity | New Level | Rationale |
|--------------------------------|-------------|-----------------|-----------|-----------|
| `SETUP_VIOLATION` | Negative setup slack (wns < 0) | `TAPEOUT_BLOCKING` (wns < -0.5ns) / `PERFORMANCE_DEGRADATION` (wns < 0) | CRITICAL / WARNING | Large violations block signoff; small violations are performance concerns |
| `HOLD_VIOLATION` | Negative hold slack (whs < 0) | `TAPEOUT_BLOCKING` | CRITICAL | Hold violations always block signoff |
| `MAX_TRANSITION` | Slow signal transitions | `TAPEOUT_BLOCKING` (>1.5ns) / `PERFORMANCE_DEGRADATION` (>0.8ns) | CRITICAL / WARNING | Threshold-dependent |
| `MAX_CAPACITANCE` | High capacitive load | `TAPEOUT_BLOCKING` (>0.5pF) / `PERFORMANCE_DEGRADATION` (>0.3pF) | CRITICAL / WARNING | Threshold-dependent |
| `CLOCK_SKEW` | Clock arrival variation | `FUNCTIONAL_RISK` (>0.8ns) / `PERFORMANCE_DEGRADATION` (>0.5ns) | ERROR / WARNING | Depends on magnitude |
| `GLOBAL_OVERFLOW` | Global routing overflow | `TAPEOUT_BLOCKING` (>10%) / `FUNCTIONAL_RISK` (>5%) | CRITICAL / ERROR | High overflow blocks routing |
| `DETAILED_OVERFLOW` | Detailed routing overflow | `TAPEOUT_BLOCKING` (>10%) / `FUNCTIONAL_RISK` (>5%) | CRITICAL / ERROR | High overflow blocks routing |
| `LAYER_CONGESTION` | Congestion on specific layer | `MEDIUM` (from signatures) | WARNING | Congestion is a concern but often fixable |
| `ROUTING_HOTSPOT` | Local routing density | `MEDIUM` (from signatures) | WARNING | Localized, usually manageable |
| `DRC_SPACING` | DRC spacing violation | `TAPEOUT_BLOCKING` | CRITICAL | DRC violations block tapeout |
| `DRC_WIDTH` | DRC width violation | `TAPEOUT_BLOCKING` | CRITICAL | DRC violations block tapeout |
| `DRC_ENCLOSURE` | DRC enclosure violation | `TAPEOUT_BLOCKING` | CRITICAL | DRC violations block tapeout |
| `DRC_ANTENNA` | Antenna rule violation | `TAPEOUT_BLOCKING` | ERROR | Fixable with antenna diode insertion |
| `DRC_DENSITY` | Metal density violation | `TAPEOUT_BLOCKING` | WARNING | Usually fixable with fill insertion |
| `LVS_OPEN_NET` | Open net in LVS | `TAPEOUT_BLOCKING` | CRITICAL | LVS failure blocks tapeout |
| `LVS_SHORT` | Short in LVS | `TAPEOUT_BLOCKING` | CRITICAL | LVS failure blocks tapeout |
| `LVS_DEVICE_MISMATCH` | Device count mismatch | `TAPEOUT_BLOCKING` | CRITICAL | LVS failure blocks tapeout |
| `LVS_PORT_MISMATCH` | Port mismatch | `TAPEOUT_BLOCKING` | CRITICAL | LVS failure blocks tapeout |
| `SRAM_PIN_BLOCKED` | SRAM macro pin blocked | `TAPEOUT_BLOCKING` | CRITICAL | Blocks routing completion |
| `UNROUTABLE_CHANNEL` | Unroutable routing channel | `TAPEOUT_BLOCKING` | CRITICAL | Routing cannot complete |
| `HALO_VIOLATION` | Macro halo violation | `TAPEOUT_BLOCKING` | CRITICAL | Blocks legal placement |
| `POWER_IR_DROP` | IR drop > threshold | `TAPEOUT_BLOCKING` (>15%) / `FUNCTIONAL_RISK` (>10%) | CRITICAL / ERROR | Depends on magnitude |
| `ELECTROMIGRATION` | EM violation | `TAPEOUT_BLOCKING` | CRITICAL | Reliability failure |
| `PDN_DISCONNECTED` | PDN open circuit | `TAPEOUT_BLOCKING` | CRITICAL | Power delivery failure |
| `CTS_SKEW` | CTS skew violation | `FUNCTIONAL_RISK` / `PERFORMANCE_DEGRADATION` | ERROR / WARNING | Depends on magnitude |
| `SLEW_VIOLATION` | Slew violation | `MEDIUM` | WARNING | Performance concern |
| `LATENCY_IMBALANCE` | Clock latency imbalance | `MEDIUM` | WARNING | Performance concern |
| `TOOL_NOT_FOUND` | EDA tool missing | `TAPEOUT_BLOCKING` | ERROR | Environment issue |
| `TOOL_BROKEN` | Tool crashed | `TAPEOUT_BLOCKING` | ERROR | Environment issue |
| `PATH_SHADOWING` | PATH shadowing | `MEDIUM` | ADVISORY | Environment oddity |
| `BROKEN_SYMLINK` | Broken symlink | `MEDIUM` | ADVISORY | Environment oddity |
| `MISSING_EXECUTABLE` | Executable not found | `HIGH` | ERROR | Environment issue |
| `CROSS_TOOL_DRC_DISAGREEMENT` | Magic vs KLayout mismatch | `MEDIUM` | WARNING | Engineering observation |
| `PIPELINE_FAILURE` | Stage crashed | `HIGH` | ERROR | Run failed to complete |
| `SIGNOFF_FAILURE` | Signoff check failed | `TAPEOUT_BLOCKING` | CRITICAL | Signoff blocker |
| `ROOT_CAUSE` | Root cause analysis | Varies | Varies | Mirrors underlying issue |

## Special Cases

| Entry Type | New Level | Note |
|-----------|-----------|------|
| Congestion hotspot (intermediate iteration) | WARNING | Intermediate routing overflows are normal |
| Antenna violation | ERROR | Usually fixable, not always a blocker |
| High fanout warning | ADVISORY | Often benign, may reduce timing margin |
| Tool disagreement (Magic vs KLayout) | WARNING | Engineering observation, not a failure |
| QoR degradation observation | WARNING | Performance concern, not a failure |
| Resolution candidate | ADVISORY | Historical learning signal |
