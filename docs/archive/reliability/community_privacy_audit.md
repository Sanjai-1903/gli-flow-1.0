# Community Intelligence — Privacy Audit

## Audit Date

2026-06-13

## Scope

Verify that the Community Intelligence escalation payload excludes all sensitive
design data: RTL, GDS, DEF, LEF, netlists, source code, and customer IP.

## Excluded Fields (Code-Level Enforcement)

The `EXCLUDED_FIELDS` list in `failure_atlas/community_intelligence/failure_package.py`
defines 12 fields that must never appear in an escalation payload:

| Field | Status |
|---|---|
| `rtl` | Blocked |
| `gds` | Blocked |
| `netlist` | Blocked |
| `source` | Blocked |
| `customer_ip` | Blocked |
| `project_files` | Blocked |
| `license` | Blocked |
| `credential` | Blocked |
| `password` | Blocked |
| `secret` | Blocked |
| `private_key` | Blocked |
| `design_files` | Blocked |

## Excluded File Extensions

The `EXCLUDED_EXTENSIONS` set blocks 12 file types:

| Extension | Content Type |
|---|---|
| `.v` | Verilog source |
| `.sv` | SystemVerilog source |
| `.vh` | Verilog header |
| `.svh` | SystemVerilog header |
| `.gds` | GDSII layout |
| `.oas` | OASIS layout |
| `.def` | Design Exchange Format |
| `.lef` | Library Exchange Format |
| `.cdl` | SPICE netlist |
| `.sp` | SPICE netlist |
| `.lib` | Liberty timing library |
| `.db` | Synopsys database |

## Design Metadata Whitelist

`FailurePackageBuilder.build()` permits only these keys from `design_metadata`:

| Allowed Key | Purpose |
|---|---|
| `design_name` | Design identifier (non-identifying) |
| `top_module` | Top-level module name |
| `pdk` | Process Design Kit name (e.g. sky130) |
| `pdk_variant` | PDK variant (e.g. sky130A) |
| `clock_period_ns` | Target clock period |
| `utilization_target` | Target cell utilization |
| `threads` | Thread count |

All other keys are silently dropped.

## Run Metadata Whitelist

`FailurePackageBuilder.build()` permits only these keys from `run_metadata`:

| Allowed Key | Purpose |
|---|---|
| `run_id` | Execution run identifier |
| `timestamp` | Run timestamp |
| `backend` | EDA backend (openroad, etc.) |
| `gli_version` | GLI-FLOW version |
| `status` | Run status |
| `current_stage` | Current pipeline stage |

All other keys are silently dropped.

## Validation

### `validate_sanitized()` Scan

Every `FailurePackage` can call `validate_sanitized()` which:

1. Serializes the entire package to JSON (lowercased)
2. Scans for each string in `EXCLUDED_FIELDS`
3. Returns warnings for any match

### Test Results

| Test | Result |
|---|---|
| RTL reference in error text flagged | PASS |
| GDS reference in error text flagged | PASS |
| Sensitive keys stripped from `design_metadata` | PASS |
| Sensitive keys stripped from `run_metadata` | PASS |
| Clean package produces zero warnings | PASS |
| Clean package has no forbidden JSON strings | PASS |

## AIContext Note

`AIContext.to_dict()` is a transparent pass-through of all fields. It does not
perform sanitization — that is delegated to `FailurePackageBuilder.build()`.
Any code path that sends `AIContext` data directly to an external API without
passing through `FailurePackageBuilder` would bypass privacy protections.

**Recommendation:** Add a `validate_sanitized()` call to `EmailWorkflow.submit()`
as a final safety check before transmitting.

## Conclusion

**PASS** — The escalation payload correctly excludes all sensitive design data.
The whitelist approach ensures that even if new metadata fields are added to
internal context objects, they will not leak into escalation packages unless
explicitly added to the allowed sets.
