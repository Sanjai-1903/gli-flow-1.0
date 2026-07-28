from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    run_id: Optional[str] = None
    tool: Optional[str] = None
    stage: Optional[str] = None
    event: str
    design_name: Optional[str] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    details: Optional[Any] = None
    recorded_at: Optional[str] = None
    created_at: Optional[str] = None
    failure_type: Optional[str] = None
    escalation_id: Optional[str] = None
    atlas_id: Optional[str] = None


class FailureAtlasEntry(BaseModel):
    run_id: str
    tool: Optional[str] = None
    stage: Optional[str] = None
    failure_type: str
    error_text: Optional[str] = None
    design_name: Optional[str] = None
    design_category: Optional[str] = None
    log_excerpt: Optional[str] = None
    frequency: int = 1
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    detected_at: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    tool_name: Optional[str] = None
    tool_stage: Optional[str] = None


class EscalationPackage(BaseModel):
    run_id: str
    package_version: str
    tool: str
    stage: str
    failure_type: str
    error_text: Optional[str] = None
    design_name: Optional[str] = None
    design_metadata: dict[str, Any] = Field(default_factory=dict)
    ai_suggestions: dict[str, Any] = Field(default_factory=dict)
    consent_record: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UploadPayload(BaseModel):
    run_id: str
    source_version: str = "1.0"
    telemetry_events: list[TelemetryEvent] = Field(default_factory=list)
    failure_atlas_entries: list[FailureAtlasEntry] = Field(default_factory=list)
    escalations: list[EscalationPackage] = Field(default_factory=list)


class UploadResponse(BaseModel):
    status: str
    run_id: str
    telemetry_accepted: int = 0
    failures_accepted: int = 0
    escalations_accepted: int = 0
    upload_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    database: str = "connected"
    uptime_sec: float = 0.0


class StatsResponse(BaseModel):
    total_telemetry_events: int = 0
    total_failure_atlas_entries: int = 0
    total_uploads: int = 0
    unique_runs: int = 0
    unique_designs: int = 0
    db_size_bytes: int = 0
