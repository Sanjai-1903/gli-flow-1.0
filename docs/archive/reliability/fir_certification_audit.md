# FIR Certification Audit

## Signoff Status: FAIL (Infrastructure Missing)

The FIR example is not currently signoff-clean because it lacks necessary design files.

## Findings

| Check | Status | Details |
| :--- | :--- | :--- |
| **Design** | **FAIL** | RTL source files missing (`examples/fir/rtl/` is empty). |
| **DRC** | N/A | Not performed |
| **LVS** | N/A | Not performed |
| **Timing** | N/A | Not performed |
| **Power** | N/A | Not performed |

## Root Cause
- **INFRASTRUCTURE:** Bundled example files are incomplete or missing.
