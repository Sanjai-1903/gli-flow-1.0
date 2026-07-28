# GCD Certification Audit

## Signoff Status: FAIL

The GCD design is not currently signoff-clean due to DRC and Power Analysis failures.

## Findings

| Check | Status | Details |
| :--- | :--- | :--- |
| **DRC** | **FAIL** | 2 violations (poly overlap of poly contact - licon.8a) |
| **LVS** | N/A | Not performed |
| **Timing** | **FAIL** | Timing reports show 'INF' slack or are inconclusive. |
| **Power** | **FAIL** | PSM-0010 Error: LU factorization of the G Matrix failed (Structurally Singular). |
| **Signoff**| **FAIL** | Multiple failures above. |

## Root Cause
- **DRC:** Physical layout violations likely due to density or placement issues.
- **Power:** The structural singularity in the power simulation suggests missing connections, floating nets, or PDK configuration issues during power analysis (PDN/PSM).
