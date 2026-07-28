# Telemetry Sanitizer Audit

> Classification of every field that can leave a user's machine.
> Generated: 2026-06-15

---

## Classification System

| Code | Meaning | Action |
|------|---------|--------|
| **SAFE** | No design IP exposure | Upload freely |
| **REDACT** | Contains design-referenced info — truncate or replace with generic placeholder | Redact before upload |
| **BLOCK** | Contains customer IP — never allowed | Reject at sanitizer level |
| **HASH** | Identifiable but must be one-way hashed to prevent reconstruction | SHA-256 before upload |
| **DERIVE** | Replace raw value with derived statistic (min/max/mean/histogram) | Compute aggregate |

---

## 1. EXECUTION METRICS

Collected by: TelemetryParser, TelemetryManager, orchestrator

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| WNS (ns) | timing.rpt, metrics.csv | **SAFE** | Numeric slack value — no IP |
| TNS (ns) | timing.rpt, metrics.csv | **SAFE** | Numeric slack value — no IP |
| Hold WNS (ns) | timing.rpt | **SAFE** | Numeric slack value |
| Hold TNS (ns) | timing.rpt | **SAFE** | Numeric slack value |
| Utilization (%) | utilization.rpt | **SAFE** | Percentage |
| Cell count | utilization.rpt | **SAFE** | Integer count |
| Runtime (sec) | runtime.rpt | **SAFE** | Duration |
| QoR score | orchestrator | **SAFE** | Composite score |
| QoR breakdown | orchestrator | **SAFE** | Component scores |
| QoR weights | orchestrator | **SAFE** | Weight values |
| Die area (µm²) | orchestrator | **SAFE** | Numeric area |
| Total power (mW) | orchestrator | **SAFE** | Numeric power |
| Internal power (mW) | orchestrator | **SAFE** | Numeric power |
| Switching power (mW) | orchestrator | **SAFE** | Numeric power |
| Leakage power (mW) | orchestrator | **SAFE** | Numeric power |
| DRC violations (count) | magic_drc.rpt, klayout_drc.xml | **SAFE** | Integer count |
| DRC magic violations | magic_drc.rpt | **SAFE** | Integer count |
| DRC klayout violations | klayout_drc.xml | **SAFE** | Integer count |
| DRC is clean (bool) | drc_lvs_summary.json | **SAFE** | Boolean |
| LVS result | drc_lvs_summary.json | **SAFE** | String (pass/fail) |
| LVS is clean (bool) | drc_lvs_summary.json | **SAFE** | Boolean |
| Setup WNS (ns) | signoff timing | **SAFE** | Numeric |
| Hold WHS (ns) | signoff timing | **SAFE** | Numeric |
| Signoff setup pass | signoff | **SAFE** | Boolean |
| Signoff hold pass | signoff | **SAFE** | Boolean |
| DRC runtime (sec) | cross_tool_drc | **SAFE** | Duration |
| LVS runtime (sec) | cross_tool_drc | **SAFE** | Duration |

---

## 2. DESIGN METADATA

Collected by: orchestrator, run manifest, AI context builder

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| Design name | manifest | **HASH** | Could identify customer project |
| Top module name | manifest | **HASH** | Could identify design hierarchy |
| PDK name | manifest | **SAFE** | Public process name (sky130A, gf180mcu) |
| PDK variant | manifest | **SAFE** | Process variant |
| Clock period (ns) | manifest | **SAFE** | Numeric |
| Utilization target (%) | manifest | **SAFE** | Percentage |
| Thread count | config | **SAFE** | Integer |
| Tool versions | environment | **SAFE** | Version strings |
| GLI version | environment | **SAFE** | Version string |

**Current behavior**: Design name and top module are sent in clear text in escalation packages (within `design_metadata` allowlist). These should be **HASHED** before upload to prevent identifying the customer's design.

---

## 3. FAILURE SIGNATURES

Collected by: SignatureEngine, Failure Atlas

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| Failure type | tool output classification | **SAFE** | Standardized string (DRC_VIOLATION, TIMING, etc.) |
| Failure signature | derived hash | **SAFE** | Already a hash of failure characteristics |
| Failure fingerprint | derived string | **SAFE** | Abstract failure pattern |
| Severity | manual/automated | **SAFE** | LOW/MEDIUM/HIGH/TAPEOUT_BLOCKING |
| Confidence | algorithm | **SAFE** | Float 0.0-1.0 |
| Error text | tool stderr/stdout | **REDACT** | May contain file paths, cell names |
| Log excerpt | log file (last 100 lines) | **REDACT** | May contain tool commands, file paths |
| Evidence JSON | multiple sources | **REDACT** | Unvalidated content |

**Current behavior**: Error text and log excerpts are sent as-is in escalation packages. Should **REDACT** file paths, register names, and cell instance paths before upload.

---

## 4. RUN METADATA

Collected by: orchestrator, run manifest

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| Run ID | generated UUID | **HASH** | Could link back to specific run |
| Timestamp | system clock | **SAFE** | ISO timestamp |
| Backend | config | **SAFE** | Tool name (openroad, etc.) |
| Status | orchestrator | **SAFE** | PENDING/RUNNING/FAILED/PASS |
| Current stage | orchestrator | **SAFE** | SYNTHESIS/FLOORPLAN/etc. |
| Flow type | config | **SAFE** | Standard flow type |

**Current behavior**: Run ID is sent in clear text. Should be **HASHED** to prevent correlating escalations back to specific runs.

---

## 5. ENVIRONMENT DATA

Collected by: EnvironmentFingerprint, ToolDiscovery

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| Tool names | tool discovery | **SAFE** | openroad, magic, klayout, etc. |
| Tool paths | environment | **REDACT** | May reveal filesystem structure |
| PDK path | environment | **REDACT** | May reveal filesystem structure |
| Total discovery duration | timer | **SAFE** | Duration in ms |
| Timeout occurred | boolean | **SAFE** | Boolean |
| Fallback count | counter | **SAFE** | Integer |
| Environment hash | derived | **SAFE** | Already hashed |
| GLI installation path | sys.path | **REDACT** | Filesystem information |

**Current behavior**: Tool paths and PDK paths may be included in error text. Should be **REDACTED** before upload.

---

## 6. AI INVESTIGATION CONTEXT

Collected by: InvestigationContextBuilder, AIContext

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| DRC violations (grouped) | magic_drc.rpt | **SAFE** | Violation type counts |
| DRC known false-positives | magic_drc.rpt | **SAFE** | Counts |
| DRC real violations | magic_drc.rpt | **SAFE** | Counts |
| LVS result summary | drc_lvs_summary.json | **SAFE** | Pass/fail + counts |
| Timing WNS/TNS | metrics.csv | **SAFE** | Numeric |
| Pipeline error type | logs/error.log | **SAFE** | OOM, tool error, config failure |
| Possible causes | derived | **SAFE** | Deterministic analysis |
| Recommended actions | derived | **SAFE** | Deterministic suggestions |
| Knowledge citations | failure_atlas_entries | **SAFE** | References |
| Investigation facts | LLM output | **SAFE** | Structured analysis |
| Possible causes (LLM) | LLM output | **SAFE** | Structured analysis |

**Current behavior**: All AI investigation context is SAFE by design. The context builder explicitly blocks source files and raw logs.

---

## 7. RESOLUTION INTELLIGENCE DATA

Collected by: ResolutionCapture, ResolutionRepository

| Field | Source | Classification | Rationale |
|-------|--------|---------------|-----------|
| Failure fingerprint | derived | **SAFE** | Abstract pattern |
| Failure type | classified | **SAFE** | Standardized string |
| Resolution description | captured | **SAFE** | Fix description |
| Resolution type | classified | **SAFE** | config_change, parameter_tweak, etc. |
| Success count | counter | **SAFE** | Integer |
| Failure count | counter | **SAFE** | Integer |
| Confidence | calculated | **SAFE** | Float 0.0-1.0 |
| Trust score | calculated | **SAFE** | Float 0.0-1.0 |
| Unique runs | counter | **SAFE** | Integer count |
| Unique designs | counter | **SAFE** | Integer count |
| Tracked run IDs | internal | **HASH** | Should hash before any upload |
| Tracked design names | internal | **HASH** | Should hash before any upload |
| Engineer confirmations | feedback | **SAFE** | Integer count |
| Contradictory reports | feedback | **SAFE** | Integer count |

**Current behavior**: Tracked run IDs and design names are stored as JSON arrays. These stay local and are used only for deduplication counting. If ever uploaded, they must be **HASHED**.

---

## 8. BLOCKED CATEGORIES (NEVER COLLECT)

These categories are explicitly blocked at the sanitizer level and should never be collected or uploaded under any circumstances:

| Category | Examples | Blocked At |
|----------|----------|-----------|
| RTL source | `.v`, `.sv`, `.vh`, `.svh` | Extension filter |
| Netlists | Verilog netlist, SPICE, CDL | Extension filter |
| Layout data | `.gds`, `.oas`, `.def`, `.lef` | Extension filter |
| Library files | `.lib`, `.db` | Extension filter |
| Bitstreams | `.bit`, `.bin`, `.bitstream` | Extension filter |
| Source code | `.c`, `.cpp`, `.py`, `.tcl`, `.sh` | Extension filter |
| Liberty files | `.lib` | Extension filter |
| Constraint files | `.sdc` | Extension filter |
| Full log files | `*.log` | Not sent — only excerpts |
| Full reports | `*.rpt` | Not sent — only parsed metrics |
| Credentials | API keys, passwords, licenses | Content scanning |
| Private keys | `*.key`, `*.pem` | Content scanning |
| Project files | `*.xpr`, `*.qpf`, project configs | Content scanning |

---

## 9. EXISTING SANITIZER EFFECTIVENESS

### What the current sanitizer does well
1. **Extension blocking**: `.v`, `.sv`, `.vh`, `.svh`, `.gds`, `.oas`, `.sp`, `.cdl`, `.def`, `.lef`, `.lib`, `.db` are all blocked
2. **Field exclusion**: `rtl`, `gds`, `netlist`, `source`, `customer_ip`, `project_files`, `license`, `credential`, `password`, `secret`, `private_key`, `design_files` are all excluded
3. **Design metadata allowlist**: Only 7 whitelisted keys pass through
4. **Run metadata allowlist**: Only 6 whitelisted keys pass through
5. **Consent gating**: 7 layers of consent enforcement
6. **Post-build validation**: `validate_sanitized()` scans serialized JSON for excluded field names
7. **AI context safety**: `InvestigationContextBuilder` uses only structured summaries, never raw files

### Gaps in the current sanitizer
1. **No path redaction**: Error text and log excerpts may contain absolute file paths that reveal filesystem structure and design names
2. **No cell/register name redaction**: Log excerpts may contain instance paths like `top/u_core/u_alu/reg_1` which could be used to infer design structure
3. **No design name hashing**: `design_name` and `top_module` are sent in clear text in escalation packages
4. **No run ID hashing**: `run_id` is sent in clear text
5. **Evidence field is opaque**: `failure_atlas_entries.evidence` is a JSON blob with no sanitization at write time
6. **validate_sanitized() is best-effort only**: Scans for field names in lowercased JSON — misses encoded or obfuscated content
7. **No regex-based redaction**: Could be more precise with regex patterns for file paths, instance paths, email addresses, IP addresses
8. **No telemetry-level sanitizer**: Sanitization only exists in the escalation path; telemetry events go through a lighter allowlist check

---

## 10. RECOMMENDED SANITIZER IMPROVEMENTS

### Priority 1: Create a standalone `TelemetrySanitizer` module
Move sanitization out of `FailurePackageBuilder` into a reusable module that can be applied at every exit point.

### Priority 2: Add path redaction
```python
# Redact absolute filesystem paths
re.sub(r'/[\w/.-]+', '<PATH_REDACTED>', text)
# Redact common home directories
re.sub(r'/home/[\w/]+', '<HOME_REDACTED>', text)
```

### Priority 3: Hash design identifiers before upload
```python
import hashlib
design_name_hash = hashlib.sha256(design_name.encode()).hexdigest()[:16]
```

### Priority 4: Hash run IDs before upload
```python
run_id_hash = hashlib.sha256(run_id.encode()).hexdigest()[:16]
```

### Priority 5: Add instance path redaction
```python
# Redact hierarchical instance paths
re.sub(r'\b\w+(?:/\w+)*/\w+\b', '<INSTANCE_PATH>', text)
```

### Priority 6: Sanitize evidence field on write
Add a hook that runs the TelemetrySanitizer on the `evidence` field before inserting into `failure_atlas_entries`.

### Priority 7: Add regex-based content scanning
Beyond field-name scanning, use regex patterns for:
- Filesystem paths (`/usr/...`, `/home/...`, `/tmp/...`)
- Email addresses
- IP addresses
- Cell instance paths
- Tool command lines with file arguments

### Priority 8: Add telemetry preview
Allow users to see the exact payload before upload (see Phase 3).
