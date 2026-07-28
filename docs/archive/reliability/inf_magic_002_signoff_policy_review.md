# INF-MAGIC-002: DRC Signoff Policy Review

**Date:** 2026-06-11
**Scope:** Current behavior, risks, and policy options for DRC signoff when cross-tool disagreement exists.

---

## Current Behavior

The signoff gate at `orchestrator.py:1156` (`release_gate_errors()`) requires **both** Magic DRC AND KLayout DRC to pass (violations == 0). If either tool reports violations, signoff is blocked:

```
orchestrator.py:882  — signoff_gate.magic_drc_pass = (magic_violations == 0)
orchestrator.py:886  — signoff_gate.klayout_drc_pass = (klayout_violations == 0)
```

This is the **Conservative** policy — no exceptions.

## Risk Analysis

### False-Positive Risk (Current Policy)

| Scenario | Magic | KLayout | Current Result | Desired Result |
|----------|-------|---------|----------------|----------------|
| Real violation | FAIL | FAIL | BLOCKED ✓ | BLOCKED |
| **Magic false-positive** | **FAIL** | **PASS** | **BLOCKED ✗** | **PASS** |
| KLayout false-positive | PASS | FAIL | BLOCKED ✗ | PASS (less likely) |
| Clean | PASS | PASS | PASS ✓ | PASS |

The GCD audit (`gcd_drc_forensic_audit.md`) proved a Magic false-positive for `licon.8a` — 2 violations that did not exist in the GDS. Under current policy, this run was blocked despite a clean KLayout result.

### Historical Impact

- **GCD run `run_1781163051_11a3ab91_gcd`**: 2 Magic licon.8a violations proven false-positive. Signoff blocked. Run marked FAILED.
- Other runs with similar edge-effect patterns may have been affected.

## Policy Options

### Option 1: Conservative (Current)
**Both tools must pass. No exceptions.**

- **Pros**: Maximum safety margin. Catches all real violations.
- **Cons**: False-positives block signoff. Requires manual intervention.
- **Effort**: None (already implemented).
- **Recommended for**: Production tapeout where risk tolerance is zero.

### Option 2: Review-Gated (Recommended)
**If tools disagree, create a Failure Atlas incident and require engineer review.**

```
if Magic FAIL and KLayout PASS:
    → CROSS_TOOL_DRC_DISAGREEMENT incident
    → DRC_REVIEW_REQUIRED state (not BLOCKED, not PASS)
    → Engineer reviews violation coordinates in GDS viewer
    → Engineer approves or rejects the violations
```

- **Pros**: False-positives don't block signoff. Knowledge base enrichment. Audit trail.
- **Cons**: Requires engineer time for review. Needs DRC_REVIEW_REQUIRED state implementation.
- **Effort**: Medium — new signoff state, API endpoints, review UI.
- **Recommended for**: Development flow, pre-tapeout validation.

### Option 3: Auto-Pass on Single-Tool Disagreement
**If Magic FAIL and KLayout PASS (or vice versa), automatically pass DRC signoff.**

- **Pros**: Zero friction. No manual intervention needed.
- **Cons**: Real violations from a single tool could be missed. Weakest integrity.
- **Effort**: Low — one conditional in signoff gate.
- **Not recommended** for any production flow.

## Recommendation

**Phase 1 (immediate)**: Keep Conservative policy. The `CrossToolDRCAnalyzer` runs at dashboard/query time only — it annotates results without modifying signoff behavior.

**Phase 2 (next sprint)**: Implement `DRC_REVIEW_REQUIRED` state:
1. Add `DRC_REVIEW_REQUIRED` to signoff gate enum
2. When `CrossToolDRCAnalyzer` detects disagreement, set signoff gate to `REVIEW_REQUIRED`
3. Create API endpoints for review approval/rejection
4. Add review frontend

**Phase 3 (future)**: After 10+ resolved disagreements, evaluate if Auto-Pass is safe for specific rule/tool combinations.

## Implementation Notes

- The `CrossToolDRCAnalyzer` at `gli_flow/core/cross_tool_drc.py` is called from the dashboard endpoint, NOT during signoff.
- To implement Review-Gated policy, call `CrossToolDRCAnalyzer.analyze()` from `orchestrator.py` DRC stage (line ~878) and check `tool_agreement` before finalizing signoff state.
- Existing signoff gate code at `orchestrator.py:1156-1189` does NOT need modification for Phase 1.
