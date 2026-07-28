# GLI-FLOW Dashboard Field Traceability

This document provides a production-grade audit trail for every metric displayed in the GLI-FLOW dashboard.

## Traceability Matrix

| Field | Source Artifact | Parser | Database Column | API Endpoint | UI Component |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Run Status** | Internal State | `FlowOrchestrator` | `runs.status` | `/runs/{run_id}` | `RunDetail` (Header) |
| **Design Name** | `gli_manifest.yaml` | `FlowOrchestrator` | `runs.design_name` | `/runs/{run_id}` | `RunDetail` (Header) |
| **PDK** | `gli_manifest.yaml` | `FlowOrchestrator` | `telemetry.pdk` | `/runs/{run_id}` | `RunDetail` (Header/Metadata) |
| **Runtime** | `metrics.csv` / `runtime.rpt` | `TelemetryParser.parse_runtime` | `runs.runtime_sec` | `/runs/{run_id}` | `SummaryTab` |
| **Die Area** | `top_floorplan_log.txt` | `TelemetryParser.parse_top_floorplan_report` | `telemetry.metrics.die_area_um2` | `/runs/{run_id}` | `AreaPowerTab` |
| **Core Area** | `block_synth_log.txt` | `TelemetryParser.parse_block_synthesis_report` | `telemetry.metrics.bs_total_area_um2` | `/runs/{run_id}` | `AreaPowerTab` |
| **Utilization** | `metrics.csv` / `utilization.rpt` | `TelemetryParser.parse_utilization` | `runs.utilization` | `/runs/{run_id}` | `AreaPowerTab` |
| **Total Power** | `power_report.txt` | `TelemetryParser.parse_power_report` | `telemetry.metrics.total_power_mw` | `/runs/{run_id}` | `AreaPowerTab` |
| **Internal Power** | `power_report.txt` | `TelemetryParser.parse_power_report` | `telemetry.metrics.internal_mw` | `/runs/{run_id}` | `AreaPowerTab` |
| **Switching Power** | `power_report.txt` | `TelemetryParser.parse_power_report` | `telemetry.metrics.switching_mw` | `/runs/{run_id}` | `AreaPowerTab` |
| **Leakage Power** | `power_report.txt` | `TelemetryParser.parse_power_report` | `telemetry.metrics.leakage_mw` | `/runs/{run_id}` | `AreaPowerTab` |
| **WNS** | `metrics.csv` / `timing.rpt` | `TelemetryParser.parse_timing` | `runs.wns` | `/runs/{run_id}` | `SummaryTab` / `TimingTab` |
| **TNS** | `metrics.csv` / `timing.rpt` | `TelemetryParser.parse_timing` | `runs.tns` | `/runs/{run_id}` | `SummaryTab` / `TimingTab` |
| **Setup Status** | Derived from WNS | `TelemetryParser.parse_timing` | `telemetry.metrics.sta_setup_status` | `/runs/{run_id}` | `TimingTab` |
| **Hold Status** | `metrics.csv` / `timing.rpt` | `TelemetryParser.parse_timing` | `telemetry.metrics.sta_hold_status` | `/runs/{run_id}` | `TimingTab` |
| **DRC Status** | `drc_raw.txt` / `drc_klayout.xml` | `TelemetryParser.parse_drc_report` | `runs.drc_is_clean` / `telemetry.metrics.drc_status` | `/runs/{run_id}` | `DrcLvsTab` |
| **DRC Runtime** | `drc_combined.json` | `drc_runner.py` | `telemetry.metrics.drc_runtime_seconds` | `/runs/{run_id}` | `DrcLvsTab` |
| **LVS Status** | `lvs_comp.out` | `TelemetryParser.parse_lvs_report` | `runs.lvs_is_clean` / `telemetry.metrics.lvs_status` | `/runs/{run_id}` | `DrcLvsTab` |
| **LVS Runtime** | `lvs_report.txt` | `OpenRoadAdapter.run_lvs` | `telemetry.metrics.lvs_runtime_seconds` | `/runs/{run_id}` | `DrcLvsTab` |
| **Antenna Status** | `antenna_report.txt` | `TelemetryParser.parse_antenna_report` | `telemetry.metrics.antenna_status` | `/runs/{run_id}` | `SummaryTab` (Signoff) |
| **EM Status** | `em_report.txt` | `TelemetryParser.parse_em_report` | `telemetry.metrics.em_status` | `/runs/{run_id}` | `SummaryTab` (Signoff) |
| **Density Status** | `density_report.txt` | `TelemetryParser.parse_density_report` | `telemetry.metrics.density_status` | `/runs/{run_id}` | `SummaryTab` (Signoff) |
| **QoR Metrics** | Multi-source | `calculate_qor_score` | `runs.qor_score` | `/runs/{run_id}` | `SummaryTab` |
| **Layout Images** | `reports/*.webp` | `OpenRoadAdapter.run_finish` | Filesystem | `/runs/{run_id}/image/{name}` | `LayoutImagesTab` |
| **Failure Atlas Entries**| `failure_atlas/*.json` | `failure_atlas.detector` | `failure_atlas_entries` | `/runs/{run_id}/failures` | `FailureAtlasTab` |

## Verification Status

- [x] Generated (Verified in `OpenRoadAdapter`)
- [x] Parsed (Verified in `TelemetryParser`)
- [x] Stored (Verified in `DatabaseManager` and `runs` table)
- [x] Served (Verified in `backend/server.py` endpoints)
- [x] Rendered (Verified in `RunDetail.jsx` and related tabs)

**Audit Verdict:** Phase 1 Complete. Full traceability confirmed.
