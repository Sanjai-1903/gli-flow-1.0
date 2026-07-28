# Telemetry Health Audit

## Root Cause Analysis
The "Failed to load telemetry health" error on the dashboard was primarily caused by a missing proxy configuration in `dashboard/vite.config.js`.

### Identified Issues
1. **Missing Vite Proxy:** The `/telemetry` prefix was not included in the Vite proxy settings, leading to 404 Not Found errors when the frontend attempted to fetch health data from `http://localhost:5173/telemetry/health`.
2. **Missing Database Table:** The `telemetry_audit_log` table was not always initialized when `TelemetryHealth` was instantiated, although it was handled gracefully by returning empty stats.
3. **Restricted Event Types:** `EscalationTelemetry` had a strict list of allowed events that excluded `ai_investigation_run` and other valid events recorded by the backend.

### Fixes Applied
- Updated `dashboard/vite.config.js` to include proxies for `/telemetry`, `/ai`, `/provenance`, and `/reliability`.
- Synchronized `EscalationTelemetry.EVENTS` with the backend's allowed event list.
- Improved UX in `TelemetryHealthPage.jsx` to show a helpful message and guidance when no telemetry has been collected yet, instead of a generic "Failed to load" error.

## API Verification
`GET /telemetry/health`
- **Status:** Healthy (returns 200 OK with valid JSON).
- **Schema:** Matches frontend expectations.
- **Example Response:**
```json
{
  "collected_events": 0,
  "events_today": 0,
  "last_event_time": null,
  "sanitized_events": 0,
  "blocked_fields": 0,
  "upload_success_rate": 1.0,
  "upload_failures": 0,
  "queued_events": 0,
  "average_upload_latency_ms": 0.0,
  "last_upload_time": null,
  "last_sanitization_time": null,
  "total_escalations": 0,
  "open_escalations": 0,
  "dataset_entries": 0,
  "resolved_unknowns": 0,
  "resolution_patterns": 0,
  "overall_status": "inactive",
  "checked_at": "..."
}
```
