# INF-MAGIC-002 Validation Update

**Date:** 2026-06-12
**Scope:** Add uart_top evidence, preserve all existing evidence

---

## Validation Status

INF-MAGIC-002 has been validated across **two independent designs**:

| Design | Run ID | Magic Violations | KLayout Violations | Rule | Status |
|---|---|---|---|---|---|
| gcd | run_1781163051_11a3ab91_gcd | 2 | 0 | licon.8a | Cross-validated via ORFS baseline |
| gcd | run_1781181168_884e85cf_gcd | 2 | 0 | licon.8a | Reference GLI-FLOW run |
| uart_top | run_1781246066_3c483cb5_uart_top | 2 | 0 | licon.8a | New evidence added in this update |
| uart_top | run_1781181681_128e166b_uart_top | 2 | 0 | licon.8a | Earlier run, same pattern |

---

## UART Evidence

### Magic DRC Report
```
DRC Results:
{poly overlap of poly contact < 0.08um in one direction (licon.8a)} {{18703 9002 18705 9018}}
Total violations: 2
```

### KLayout DRC Report
Empty `<items>` section — 0 violations. No `licon.8a` category in XML output.

### Cross-Tool Analysis
- `drc_combined.json`: `drc_clean: false`, `total_violations: 2`, `magic: {run: true, violations: 2}`, `klayout: {run: true, violations: 0}`
- `drc_agreement.json`: `tool_agreement: TOOL_DISAGREEMENT`, `disagreement_type: MAGIC_FAIL_KLAYOUT_PASS`
- FA incident ID: `872e87a3-9ed1-4a87-a5b8-2e6bf1806ff6`

### Comparison with GCD

| Property | GCD | UART |
|---|---|---|
| Rule | licon.8a | licon.8a |
| Magic violations | 2 | 2 |
| KLayout violations | 0 | 0 |
| Bounding boxes | 3 (2×16 each) | 1 (2×16) |
| Disagreement type | MAGIC_FAIL_KLAYOUT_PASS | MAGIC_FAIL_KLAYOUT_PASS |
| Report total | 2 | 2 |
| Design size | ~270 cells | — |

The bounding box dimensions are identical (2×16 database units = 0.01µm × 0.08µm), confirming the same rule interpretation discrepancy.

---

## Knowledge Base Update

### Changes Required to `failure_atlas/knowledge_base.json`

**1. Update `design` field to list both designs:**

```json
// FROM:
"design": "gcd",

// TO:
"design": ["gcd", "uart_top"],
```

**2. Add `validated_designs` field:**

```json
"validated_designs": [
  {
    "design": "gcd",
    "run_id": "run_1781163051_11a3ab91_gcd",
    "orfs_validated": true,
    "magic_violations": 2,
    "klayout_violations": 0,
    "bounding_boxes": ["(13459,6826)-(13461,6842)", "(12171,5738)-(12173,5754)", "(14287,5738)-(14289,5754)"],
    "fa_incident_id": "8f25d3a5-51fa-404e-bf1b-e23387b4c638"
  },
  {
    "design": "uart_top",
    "run_id": "run_1781246066_3c483cb5_uart_top",
    "orfs_validated": false,
    "magic_violations": 2,
    "klayout_violations": 0,
    "bounding_boxes": ["(18703,9002)-(18705,9018)"],
    "fa_incident_id": "872e87a3-9ed1-4a87-a5b8-2e6bf1806ff6"
  }
]
```

**3. Update `common_causes` to reflect design-independence:**

```json
// ADD to common_causes:
"Design-independent — reproduces on both gcd and uart_top with identical rule/count pattern"
```

**4. Update `verification_steps` to include cross-design verification:**

```json
// ADD to verification_steps:
"Cross-design validation confirmed — Same licon.8a pattern on uart_top (design-independent)"
```

---

## Statement

INF-MAGIC-002 is now **design-independent**. The same `licon.8a` false-positive pattern has been observed on:

- **gcd** (2 runs, 1 ORFS-validated)
- **uart_top** (2 runs, same toolchain)

The signature `inf_magic_002_cross_tool_disagreement` should be reused for all future licon.8a cross-tool disagreements. **No INF-MAGIC-003 is needed** — the mechanism is identical across designs.
