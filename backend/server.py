from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from pathlib import Path

import dataclasses
import json
import math
import mimetypes
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from gli_flow.database.factory import create_provider
from gli_flow.database.database_provider import DatabaseProvider, Row
from gli_flow.database.sqlite import DatabaseManager
from gli_flow.investigation.availability import InvestigationAvailabilityService, ENV_KEY_NAME
from gli_flow.resolution_intelligence import (
    ResolutionRepository,
    ResolutionCapture,
    ResolutionScorer,
    TrustScorer,
    RunComparisonEngine,
    AtlasCandidateGenerator,
)

app = FastAPI()

allowed_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_provider() -> DatabaseProvider:
    provider = create_provider()
    provider.migrate()
    return provider


def get_connection():
    return _BackendConnection(get_provider())


def validate_schema_at_startup():
    provider = get_provider()
    try:
        ok = provider.validate_schema()
        if not ok:
            raise RuntimeError("Database schema validation failed")
    finally:
        provider.close()


class _BackendConnection:
    """Compatibility wrapper that lets existing backend code use DatabaseProvider
    with minimal changes. Provides cursor-like interface."""
    def __init__(self, provider: DatabaseProvider):
        self._provider = provider

    def cursor(self):
        return _BackendCursor(self._provider)

    def close(self):
        self._provider.close()

    def commit(self):
        pass

    def rollback(self):
        self._provider.rollback()

    @property
    def provider(self):
        return self._provider


class _RowAdapter:
    """Wraps a dict row to support both key and index access."""
    def __init__(self, data: dict, columns: list):
        self._data = data
        self._columns = columns
        self._values = tuple(data.get(c) for c in columns) if columns else tuple(data.values())

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._values[key]
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def get(self, key, default=None):
        return self._data.get(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)


class _BackendCursor:
    def __init__(self, provider: DatabaseProvider):
        self._provider = provider
        self._rows: List[Row] = []
        self._index = 0
        self._description: List[Any] = []
        self._sql = ""
        self._params: Optional[Any] = None

    def execute(self, sql: str, params: Any = None):
        self._sql = sql
        self._params = params
        self._rows = []
        self._index = 0
        pg_sql = _normalize_sql(sql)
        if params is not None:
            rows = self._provider.fetchall(pg_sql, params)
        else:
            rows = self._provider.fetchall(pg_sql)
        if rows:
            cols = list(rows[0].keys())
            self._description = [(k,) for k in cols]
            self._rows = [_RowAdapter(r, cols) for r in rows]
        return self

    def executemany(self, sql: str, seq_of_params: List[Any]):
        pg_sql = _normalize_sql(sql)
        for params in seq_of_params:
            self._provider.execute(pg_sql, params)
        return self

    def fetchone(self) -> Optional[Row]:
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        return None

    def fetchall(self) -> List[Row]:
        result = self._rows[self._index:]
        self._index = len(self._rows)
        return result

    def fetchmany(self, size: int = 1) -> List[Row]:
        result = self._rows[self._index:self._index + size]
        self._index += len(result)
        return result

    @property
    def description(self):
        return self._description

    @property
    def rowcount(self) -> int:
        return len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def close(self):
        pass


def _normalize_sql(sql: str) -> str:
    if not sql:
        return sql
    url = os.environ.get("DATABASE_URL", "")
    if url.startswith("postgresql"):
        return sql.replace("?", "%s")
    return sql


def rows_to_dicts(rows, columns):
    if not rows:
        return []
    if isinstance(rows[0], dict):
        return rows
    if hasattr(rows[0], '_data'):
        return [r._data for r in rows]
    return [dict(zip(columns, row)) for row in rows]


def row_to_dict(row):
    if row is None:
        return None
    if isinstance(row, dict):
        d = dict(row)
    else:
        d = dict(row)
    for field in ("evidence", "recommended_fix", "before_metrics", "after_metrics"):
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    if isinstance(d.get("fix_applied"), int):
        d["fix_applied"] = bool(d["fix_applied"])
    if isinstance(d.get("fix_applied"), bool):
        pass
    return d


def _sanitize(obj):
    if isinstance(obj, float):
        import math
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


def _safe_run_path(run_id: str, *parts: str) -> Path:
    run_dir = (_OUTPUTS_DIR / run_id).resolve()
    candidate = run_dir.joinpath(*parts).resolve()
    if candidate != run_dir and run_dir not in candidate.parents:
        raise HTTPException(status_code=400, detail="Invalid path")
    return candidate


validate_schema_at_startup()


# --------------------------------------------------
# AI investigation startup validation
# --------------------------------------------------
_ai_availability_service = InvestigationAvailabilityService()
_ai_health = _ai_availability_service.check_availability()
if _ai_health.is_ready:
    print(f"✓ BharatCode connected (provider: {_ai_health.provider})")
elif not _ai_health.api_key_present:
    print(f"✗ BharatCode API key missing — set {ENV_KEY_NAME} in .env")
elif not _ai_health.api_key_valid:
    print("✗ BharatCode API key is a placeholder or invalid — set a real API key")
elif _ai_health.status in ("MISCONFIGURED", "UNAVAILABLE"):
    print(f"✗ BharatCode {_ai_health.reason} — {_ai_health.fix}")
else:
    print(f"✗ BharatCode unavailable: {_ai_health.reason}")
# --------------------------------------------------


@app.get("/runs")
def get_runs(limit: int = Query(50, ge=1, le=10000), important: bool = Query(False)):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            SELECT
                r.run_id,
                r.design_name,
                r.status,
                r.current_stage,
                r.progress,
                r.wns,
                r.tns,
                r.hold_wns,
                r.hold_tns,
                r.utilization,
                r.runtime_sec,
                r.cell_count,
                r.qor_score,
                r.timestamp,
                r.is_important,
                r.tapeout_ready,
                r.implementation_status,
                r.signoff_status,
                r.implementation_score,
                r.signoff_score,
                r.root_cause_summary,
                r.drc_violations,
                r.drc_is_clean,
                r.lvs_is_clean,
                COALESCE(fa.failure_count, 0) AS failure_count,
                COALESCE(fa.severest, '') AS max_severity
            FROM runs r
            LEFT JOIN (
                SELECT run_id, COUNT(*) AS failure_count,
                 MAX(CASE severity
                          WHEN 'TAPEOUT_BLOCKING' THEN 5
                          WHEN 'HIGH' THEN 4
                          WHEN 'UNDER_REVIEW' THEN 3
                          WHEN 'FUNCTIONAL_RISK' THEN 3
                          WHEN 'PERFORMANCE_DEGRADATION' THEN 2
                          WHEN 'MEDIUM' THEN 1
                          WHEN 'LOW' THEN 0
                          ELSE -1 END) AS severity_rank,
                       MAX(severity) AS severest
                FROM failure_atlas_entries
                GROUP BY run_id
            ) fa ON r.run_id = fa.run_id
        """
        params = []
        if important:
            sql += " WHERE r.is_important = 1"
        
        sql += " ORDER BY r.timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        columns = [
            "run_id", "design_name", "status", "current_stage",
            "progress", "wns", "tns", "hold_wns", "hold_tns",
            "utilization", "runtime_sec", "cell_count", "qor_score",
            "timestamp", "is_important", "tapeout_ready",
            "implementation_status", "signoff_status",
            "implementation_score", "signoff_score", "root_cause_summary",
            "drc_violations", "drc_is_clean", "lvs_is_clean",
            "failure_count", "max_severity",
        ]
        return rows_to_dicts(rows, columns)
    finally:
        conn.close()


@app.get("/runs/count")
def get_runs_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM runs")
        return {"total": cursor.fetchone()[0]}
    finally:
        conn.close()


@app.get("/live_runs")
def get_live_runs():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                run_id,
                status,
                current_stage,
                progress
            FROM runs
            WHERE status='RUNNING'
            ORDER BY timestamp DESC
            """
        )
        rows = cursor.fetchall()
        columns = ["run_id", "status", "current_stage", "progress"]
        return rows_to_dicts(rows, columns)
    finally:
        conn.close()


@app.get("/trends")
def get_trends():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                qor_score,
                runtime_sec
            FROM runs
            WHERE qor_score IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 20
            """
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    if len(rows) == 0:
        return {
            "trend": "NO_DATA",
            "avg_qor": 0,
            "avg_runtime": 0,
            "regressions": 0
        }

    qor_values = [row[0] for row in rows if row[0] is not None]
    runtime_values = [row[1] for row in rows if row[1] is not None]

    avg_qor = round(
        sum(qor_values) / len(qor_values), 2
    ) if qor_values else 0

    avg_runtime = round(
        sum(runtime_values) / len(runtime_values), 2
    ) if runtime_values else 0

    regressions = len(
        [v for v in qor_values if v < 0.7]
    )

    if len(qor_values) >= 2:
        if qor_values[0] > qor_values[-1]:
            trend = "IMPROVING"
        elif qor_values[0] < qor_values[-1]:
            trend = "DEGRADING"
        else:
            trend = "STABLE"
    else:
        trend = "NO_DATA"

    return {
        "trend": trend,
        "avg_qor": avg_qor,
        "avg_runtime": avg_runtime,
        "regressions": regressions
    }


_OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs" / "runs"


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                run_id, design_name, status, current_stage, progress,
                wns, tns, hold_wns, hold_tns, utilization, runtime_sec,
                cell_count, qor_score, timestamp, drc_violations,
                drc_magic_violations, drc_klayout_violations, drc_is_clean,
                lvs_result, lvs_is_clean, signoff_setup_pass, signoff_hold_pass,
                signoff_gate_json, tapeout_ready, implementation_status,
                signoff_status, implementation_score, signoff_score,
                root_cause_summary
            FROM runs
            WHERE run_id = ?
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Run not found")
        columns = [
            "run_id", "design_name", "status", "current_stage",
            "progress", "wns", "tns", "hold_wns", "hold_tns",
            "utilization", "runtime_sec", "cell_count", "qor_score",
            "timestamp", "drc_violations", "drc_magic_violations",
            "drc_klayout_violations", "drc_is_clean", "lvs_result",
            "lvs_is_clean", "signoff_setup_pass", "signoff_hold_pass",
            "signoff_gate_json", "tapeout_ready", "implementation_status",
            "signoff_status", "implementation_score", "signoff_score",
            "root_cause_summary",
        ]
        result = dict(zip(columns, row))

        cursor.execute(
            "SELECT COUNT(*), MAX(severity) FROM failure_atlas_entries WHERE run_id = ?",
            (run_id,),
        )
        fa_row = cursor.fetchone()
        result["failure_count"] = fa_row[0] or 0
        result["max_severity"] = fa_row[1] or ""

        run_dir = _OUTPUTS_DIR / run_id
        if run_dir.is_dir():
            result["run_dir"] = str(run_dir)
            artifacts = []
            for f in sorted(run_dir.rglob("*")):
                if f.is_file() and f.suffix in (".json", ".csv", ".rpt", ".txt", ".log", ".gds", ".def", ".v", ".webp", ".png", ".jpg"):
                    rel = f.relative_to(run_dir)
                    artifacts.append(str(rel))
            result["artifacts"] = artifacts
            drc_lvs_path = run_dir / "drc_lvs_summary.json"
            if drc_lvs_path.exists():
                result["drc_lvs"] = _sanitize(json.loads(drc_lvs_path.read_text()))
            classification_path = run_dir / "signoff_classification.json"
            if classification_path.exists():
                try:
                    result["signoff_classification"] = _sanitize(json.loads(classification_path.read_text()))
                except Exception:
                    pass
            drc_combined_path = run_dir / "reports" / "drc_combined.json"
            if drc_combined_path.exists():
                try:
                    result["drc_combined"] = _sanitize(json.loads(drc_combined_path.read_text()))
                except Exception:
                    pass
            drc_agreement_path = run_dir / "telemetry" / "drc_agreement.json"
            if drc_agreement_path.exists():
                try:
                    result["drc_analysis"] = _sanitize(json.loads(drc_agreement_path.read_text()))
                except Exception:
                    pass
            sta_path = run_dir / "sta_corners.json"
            if sta_path.exists():
                result["sta_corners"] = _sanitize(json.loads(sta_path.read_text()))
            telemetry_path = run_dir / "telemetry" / "metrics.json"
            if telemetry_path.exists():
                result["telemetry"] = _sanitize(json.loads(telemetry_path.read_text()))
        return result
    finally:
        conn.close()


@app.get("/runs/{run_id}/drc")
def get_run_drc(run_id: str):
    run_dir = _OUTPUTS_DIR / run_id
    if not run_dir.is_dir():
        raise HTTPException(status_code=404, detail="Run directory not found")
    drc_combined_path = run_dir / "reports" / "drc_combined.json"
    if not drc_combined_path.exists():
        return {"run_id": run_id, "drc_result": None, "analysis": None}
    try:
        drc_combined = json.loads(drc_combined_path.read_text())
        analysis = None
        drc_agreement_path = run_dir / "telemetry" / "drc_agreement.json"
        if drc_agreement_path.exists():
            analysis = json.loads(drc_agreement_path.read_text())
        return {"run_id": run_id, "drc_result": _sanitize(drc_combined), "analysis": _sanitize(analysis)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="DRC analysis error — run data may be incomplete or corrupt")


@app.get("/runs/{run_id}/image/{image_name:path}")
def get_run_image(run_id: str, image_name: str):
    for ext in ("", ".webp", ".png", ".jpg", ".webp.png", ".svg"):
        candidate = _safe_run_path(run_id, "reports", image_name + ext)
        if candidate.exists():
            mime = _image_mime_type(candidate)
            return FileResponse(str(candidate), media_type=mime)
        candidate = _safe_run_path(run_id, image_name + ext)
        if candidate.exists():
            mime = _image_mime_type(candidate)
            return FileResponse(str(candidate), media_type=mime)
    raise HTTPException(status_code=404, detail="Image not found")


def _image_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".webp":
        return "image/webp"
    if ext == ".png":
        return "image/png"
    if ext == ".jpg" or ext == ".jpeg":
        return "image/jpeg"
    if ext == ".svg":
        return "image/svg+xml"
    return "image/webp"


_EMPTY_REPORT_FALLBACKS = {
    "antenna": "0 antenna violations",
    "atpg": "ATPG tool not available — 0 patterns generated",
    "drc": "0 DRC violations",
    "violation": "0 violations",
}

def _report_text(text: str, report_type: str) -> str:
    stripped = text.strip()
    if stripped:
        return text
    report_lower = report_type.lower()
    for keyword, msg in _EMPTY_REPORT_FALLBACKS.items():
        if keyword in report_lower:
            return msg + "\n"
    return "No data\n"

@app.get("/runs/{run_id}/report/{report_type:path}")
def get_run_report(run_id: str, report_type: str):
    direct = _safe_run_path(run_id, report_type)
    if direct.exists():
        if direct.suffix in (".json", ".csv", ".log", ".txt", ".rpt"):
            text = _report_text(direct.read_text(errors="replace"), report_type)
            return PlainTextResponse(text)
        return FileResponse(str(direct))
    for fname in (report_type, report_type + ".rpt", report_type + ".txt", report_type + ".csv", report_type + ".json", report_type + ".log"):
        candidate = _safe_run_path(run_id, "reports", fname)
        if candidate.exists():
            if candidate.suffix in (".json", ".csv", ".log", ".txt", ".rpt"):
                text = _report_text(candidate.read_text(errors="replace"), report_type)
                return PlainTextResponse(text)
            return FileResponse(str(candidate))
    artifacts_file = _safe_run_path(run_id, "artifacts", report_type)
    if artifacts_file.exists():
        return FileResponse(str(artifacts_file))
    raise HTTPException(status_code=404, detail="Report not found")


# ── Artifact Viewer Endpoints ───────────────────────────────────────────────

TEXT_EXTENSIONS = {".txt", ".log", ".rpt", ".csv", ".json", ".yaml", ".yml",
                   ".md", ".v", ".sv", ".vhdl", ".tcl", ".py", ".cfg", ".conf",
                   ".sdc", ".sdf", ".spef", ".lib", ".lef", ".def"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
PDF_EXTENSIONS = {".pdf"}
HTML_EXTENSIONS = {".html", ".htm"}

ARTIFACT_CATEGORIES = {
    "reports": {".rpt", ".txt", ".csv", ".md"},
    "logs": {".log"},
    "images": IMAGE_EXTENSIONS,
    "pdfs": PDF_EXTENSIONS,
    "html": HTML_EXTENSIONS,
    "json": {".json"},
    "yaml": {".yaml", ".yml"},
    "config": {".cfg", ".conf", ".tcl", ".sdc"},
    "code": {".v", ".sv", ".vhdl", ".py"},
    "layout": {".gds", ".def", ".lef", ".lib", ".sdf", ".spef", ".spi"},
}


def _artifact_mime_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return _image_mime_type(path)
    if ext == ".pdf":
        return "application/pdf"
    if ext in (".html", ".htm"):
        return "text/html"
    if ext == ".json":
        return "application/json"
    if ext == ".csv":
        return "text/csv"
    if ext == ".yaml" or ext == ".yml":
        return "text/yaml"
    if ext == ".svg":
        return "image/svg+xml"
    if ext in (".gds",):
        return "application/octet-stream"
    if ext in (".def", ".lef", ".lib", ".sdc", ".sdf", ".spef", ".spi"):
        return "text/plain"
    mt = mimetypes.guess_type(str(path))[0]
    return mt or "application/octet-stream"


def _categorize_artifact(ext: str) -> str:
    for cat, exts in ARTIFACT_CATEGORIES.items():
        if ext in exts:
            return cat
    return "other"


@app.get("/runs/{run_id}/artifacts")
def list_artifacts(run_id: str):
    # Try primary run directory path
    run_dir = _OUTPUTS_DIR / run_id

    # Fallback: check database for the run's run_dir if it differs
    if not run_dir.is_dir():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT run_dir FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                alt = Path(row[0])
                if alt.is_dir():
                    run_dir = alt
        except Exception:
            pass

    artifacts = []
    if not run_dir.is_dir():
        return artifacts

    for f in sorted(run_dir.rglob("*")):
        if not f.is_file() or f.name.startswith("."):
            continue
        rel = str(f.relative_to(run_dir))
        ext = f.suffix.lower()
        stat = f.stat()
        artifacts.append({
            "path": rel,
            "name": f.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 3),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": ext,
            "category": _categorize_artifact(ext),
            "is_text": ext in TEXT_EXTENSIONS,
            "is_image": ext in IMAGE_EXTENSIONS,
            "is_pdf": ext in PDF_EXTENSIONS,
            "is_html": ext in HTML_EXTENSIONS,
        })
    return artifacts


@app.get("/runs/{run_id}/artifact")
def get_artifact_file(run_id: str, path: str = Query(...)):
    safe = _safe_run_path(run_id, path)
    if not safe.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found")
    mime = _artifact_mime_type(safe)
    return FileResponse(str(safe), media_type=mime, filename=safe.name)


@app.get("/runs/{run_id}/artifact/preview")
def get_artifact_preview(
    run_id: str,
    path: str = Query(...),
    max_preview_mb: float = Query(5.0, ge=0.1, le=100),
    lines: int = Query(0, ge=0, le=100000),
):
    safe = _safe_run_path(run_id, path)
    if not safe.is_file():
        raise HTTPException(status_code=404, detail="Artifact not found")
    ext = safe.suffix.lower()
    if ext not in TEXT_EXTENSIONS:
        raise HTTPException(status_code=400,
                            detail=f"Preview not supported for {ext} files. Use /artifact endpoint for raw file.")
    stat = safe.stat()
    size_mb = stat.st_size / (1024 * 1024)
    truncated = False
    content = safe.read_text(errors="replace")
    if size_mb > max_preview_mb:
        max_chars = int(max_preview_mb * 1024 * 1024)
        content = content[:max_chars]
        truncated = True
    if lines > 0:
        content_lines = content.splitlines(keepends=True)
        content = "".join(content_lines[:lines])
        if len(content_lines) > lines:
            truncated = True
    return {
        "content": content,
        "size_bytes": stat.st_size,
        "size_mb": round(size_mb, 3),
        "truncated": truncated,
        "line_count": content.count("\n") + 1 if content else 0,
    }


@app.get("/releases")
def get_releases():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT run_id, design_name, qor_score, status, timestamp
            FROM runs
            WHERE qor_score IS NOT NULL
            ORDER BY qor_score DESC
            LIMIT 10
            """
        )
        rows = cursor.fetchall()
        columns = ["run_id", "design_name", "qor_score", "status", "timestamp"]
        return rows_to_dicts(rows, columns)
    finally:
        conn.close()


@app.get("/health")
def get_health():
    tools = {}
    for name in ("openroad", "yosys", "klayout", "magic", "netgen"):
        tools[name] = shutil.which(name) is not None
    db_path = get_production_db_path()
    return {
        "status": "ok",
        "database": os.path.isfile(db_path),
        "tools": tools,
    }


# ====================================================
# FAILURE ATLAS API ENDPOINTS
# ====================================================

def get_classification_filter(include_heuristic: bool = False, include_unverified: bool = False):
    classifications = ["VERIFIED"]
    if include_heuristic:
        classifications.append("HEURISTIC")
    if include_unverified:
        classifications.append("UNVERIFIED")
    return classifications


from failure_atlas.run_trust_engine import RunTrustEngine
import os
from pathlib import Path

# Helper to get production DB path
def get_production_db_path():
    return os.environ.get("GLI_FLOW_DB") or str(Path.home() / ".gli_flow" / "gli_flow.db")

@app.get("/runs/{run_id}/trust-score")
def get_run_trust_score(run_id: str):
    engine = RunTrustEngine(get_production_db_path())
    return engine.compute_run_trust_score(run_id)
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM failure_atlas_entries WHERE run_id = ? AND detection_classification IN ({placeholders}) ORDER BY detected_at DESC",
            (run_id, *classifications),
        )
        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@app.get("/failures")
def get_failures(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    severity: str = Query(None),
    failure_type: str = Query(None),
    search: str = Query(None),
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        query = f"""
            SELECT fa.*, r.is_important 
            FROM failure_atlas_entries fa
            LEFT JOIN runs r ON fa.run_id = r.run_id
            WHERE fa.detection_classification IN ({placeholders})
        """
        count_query = f"SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({placeholders})"
        params = list(classifications)

        if severity:
            query += " AND severity = ?"
            count_query += " AND severity = ?"
            params.append(severity)
        if failure_type:
            query += " AND failure_type = ?"
            count_query += " AND failure_type = ?"
            params.append(failure_type)
        if search:
            query += " AND (title LIKE ? OR description LIKE ? OR failure_type LIKE ?)"
            count_query += " AND (title LIKE ? OR description LIKE ? OR failure_type LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        query += " ORDER BY detected_at DESC LIMIT ? OFFSET ?"
        cursor.execute(query, params + [limit, offset])
        
        # Need to map columns manually to dict
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Apply row_to_dict logic
        for r in results:
            # Reconstruct the dict to handle JSON fields
            for field in ("evidence", "recommended_fix", "before_metrics", "after_metrics"):
                if r.get(field) and isinstance(r[field], str):
                    try:
                        r[field] = json.loads(r[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            if isinstance(r.get("fix_applied"), int):
                r["fix_applied"] = bool(r["fix_applied"])

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results,
        }
    finally:
        conn.close()


@app.get("/runs/{run_id}/failures")
def get_run_failures(
    run_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        query = f"""
            SELECT fa.*, r.is_important
            FROM failure_atlas_entries fa
            LEFT JOIN runs r ON fa.run_id = r.run_id
            WHERE fa.run_id = ? AND fa.detection_classification IN ({placeholders})
        """
        count_query = f"SELECT COUNT(*) FROM failure_atlas_entries WHERE run_id = ? AND detection_classification IN ({placeholders})"

        cursor.execute(count_query, [run_id] + list(classifications))
        total = cursor.fetchone()[0]

        query += " ORDER BY detected_at DESC LIMIT ? OFFSET ?"
        cursor.execute(query, [run_id] + list(classifications) + [limit, offset])

        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for r in results:
            for field in ("evidence", "recommended_fix", "before_metrics", "after_metrics"):
                if r.get(field) and isinstance(r[field], str):
                    try:
                        r[field] = json.loads(r[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            if isinstance(r.get("fix_applied"), int):
                r["fix_applied"] = bool(r["fix_applied"])

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results,
        }
    finally:
        conn.close()


@app.get("/failures/{failure_id}")
def get_failure(failure_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM failure_atlas_entries WHERE id = ?",
            (failure_id,),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute(
                "SELECT * FROM failure_atlas_entries WHERE failure_id = ?",
                (failure_id,),
            )
            row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Failure not found")
        result = row_to_dict(row)

        related = conn.cursor()
        related.execute(
            "SELECT * FROM failure_atlas_entries WHERE failure_type = ? AND id != ? ORDER BY detected_at DESC LIMIT 5",
            (result["failure_type"], result["id"]),
        )
        result["similar_failures"] = [row_to_dict(r) for r in related.fetchall()]

        return result
    finally:
        conn.close()


@app.post("/failures/{failure_id}/resolution")
def resolve_failure(failure_id: str, payload: dict):
    fix_type = payload.get("fix_type")
    fix_description = payload.get("fix_description", "")
    fix_run_id = payload.get("fix_run_id", "")
    before_metrics = payload.get("before_metrics")
    after_metrics = payload.get("after_metrics")

    if not fix_type:
        raise HTTPException(status_code=400, detail="fix_type is required")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM failure_atlas_entries WHERE id = ? OR failure_id = ?",
            (failure_id, failure_id),
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Failure not found")

        actual_id = row[0]

        before_json = json.dumps(before_metrics) if before_metrics else None
        after_json = json.dumps(after_metrics) if after_metrics else None

        resolution_confidence = "MEDIUM"
        if before_metrics and after_metrics:
            wns_before = before_metrics.get("wns", 0.0)
            wns_after = after_metrics.get("wns", 0.0)
            if wns_after > wns_before:
                resolution_confidence = "HIGH"
            else:
                resolution_confidence = "LOW"

        cursor.execute(
            """
            UPDATE failure_atlas_entries SET
                fix_applied = 1,
                fix_type = ?,
                fix_description = ?,
                fix_run_id = ?,
                before_metrics = ?,
                after_metrics = ?,
                resolution_confidence = ?
            WHERE id = ?
            """,
            (fix_type, fix_description, fix_run_id,
             before_json, after_json, resolution_confidence,
             actual_id),
        )
        conn.commit()

        return {"status": "ok", "message": "Resolution recorded", "resolution_confidence": resolution_confidence}
    finally:
        conn.close()


# ====================================================
# ANALYTICS ENDPOINTS
# ====================================================

@app.get("/analytics/summary")
def get_analytics_summary(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({placeholders})", classifications)
        total = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE fix_applied = 1 AND detection_classification IN ({placeholders})", classifications)
        fixed = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM failure_atlas_entries WHERE resolution_confidence = 'HIGH' AND detection_classification IN ({placeholders})", classifications)
        high_confidence = cursor.fetchone()[0]

        return {
            "total_failures": total,
            "fixed_count": fixed,
            "unfixed_count": total - fixed,
            "success_rate": round(fixed / total * 100, 1) if total > 0 else 0,
            "high_confidence_resolutions": high_confidence,
        }
    finally:
        conn.close()


@app.get("/analytics/common-failures")
def get_common_failures(
    limit: int = Query(10, ge=1, le=50),
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT failure_type, COUNT(*) as count,
                   ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({placeholders})) * 100, 1) as percentage
            FROM failure_atlas_entries
            WHERE detection_classification IN ({placeholders})
            GROUP BY failure_type
            ORDER BY count DESC
            LIMIT ?
            """,
            (*classifications, *classifications, limit),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@app.get("/analytics/fix-effectiveness")
def get_fix_effectiveness(
    min_samples: int = Query(3, ge=1),
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT failure_type, fix_type,
                   COUNT(*) as sample_size,
                   ROUND(CAST(SUM(fix_applied) AS FLOAT) / COUNT(*) * 100, 1) as success_rate
            FROM failure_atlas_entries
            WHERE fix_type IS NOT NULL AND fix_type != ''
            AND detection_classification IN ({placeholders})
            GROUP BY failure_type, fix_type
            HAVING sample_size >= ?
            ORDER BY success_rate DESC
            """,
            (*classifications, min_samples),
        )
        results = [dict(row) for row in cursor.fetchall()]
        if not results:
            return {"message": "Insufficient Data", "min_samples_required": min_samples, "results": []}
        return {"results": results, "min_samples": min_samples}
    finally:
        conn.close()


@app.get("/analytics/qor-improvements")
def get_qor_improvements(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT fix_type,
                   COUNT(*) as sample_size,
                   COALESCE(AVG(
                       CASE
                           WHEN before_metrics IS NOT NULL AND after_metrics IS NOT NULL
                           THEN json_extract(after_metrics, '$.wns') - json_extract(before_metrics, '$.wns')
                           ELSE NULL
                       END
                   ), 0) as avg_wns_improvement,
                   COALESCE(AVG(
                       CASE
                           WHEN before_metrics IS NOT NULL AND after_metrics IS NOT NULL
                           THEN json_extract(after_metrics, '$.tns') - json_extract(before_metrics, '$.tns')
                           ELSE NULL
                       END
                   ), 0) as avg_tns_improvement
            FROM failure_atlas_entries
            WHERE fix_type IS NOT NULL AND fix_type != ''
            AND detection_classification IN ({placeholders})
            GROUP BY fix_type
            ORDER BY avg_wns_improvement DESC
            """,
            classifications,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


@app.get("/analytics/failure-trends")
def get_failure_trends(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT failure_type, COUNT(*) as count,
                   ROUND(CAST(COUNT(*) AS FLOAT) / (SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification IN ({placeholders})) * 100, 1) as percentage
            FROM failure_atlas_entries
            WHERE detection_classification IN ({placeholders})
            GROUP BY failure_type
            ORDER BY count DESC
            """,
            (*classifications, *classifications),
        )
        failure_dist = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            f"""
            SELECT DATE(detected_at) as date, COUNT(*) as count
            FROM failure_atlas_entries
            WHERE detected_at IS NOT NULL
            AND detection_classification IN ({placeholders})
            GROUP BY DATE(detected_at)
            ORDER BY date DESC
            LIMIT 30
            """,
            classifications,
        )
        daily_counts = [dict(row) for row in cursor.fetchall()]

        return {
            "failure_distribution": failure_dist,
            "daily_counts": daily_counts,
        }
    finally:
        conn.close()


@app.get("/analytics/resolution-confidence")
def get_resolution_confidence(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT resolution_confidence, COUNT(*) as count
            FROM failure_atlas_entries
            WHERE resolution_confidence IS NOT NULL
            AND detection_classification IN ({placeholders})
            GROUP BY resolution_confidence
            ORDER BY count DESC
            """,
            classifications,
        )
        distribution = [dict(row) for row in cursor.fetchall()]

        cursor.execute(
            f"""
            SELECT COUNT(*) FROM failure_atlas_entries
            WHERE (resolution_confidence IS NULL OR resolution_confidence = '')
            AND detection_classification IN ({placeholders})
            """,
            classifications,
        )
        unresolved = cursor.fetchone()[0]

        return {
            "distribution": distribution,
            "unresolved": unresolved,
        }
    finally:
        conn.close()


@app.get("/analytics/mttr")
def get_mttr(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT failure_type,
                   COUNT(*) as sample_size,
                   ROUND(CAST(SUM(CASE WHEN fix_applied = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as resolution_rate
            FROM failure_atlas_entries
            WHERE detection_classification IN ({placeholders})
            GROUP BY failure_type
            ORDER BY sample_size DESC
            """,
            classifications,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ====================================================
# REGRESSION EVENTS
# ====================================================

@app.get("/regressions")
def get_regressions(
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT f1.*
            FROM failure_atlas_entries f1
            WHERE f1.detection_classification IN ({placeholders})
            AND f1.detected_at = (
                SELECT MIN(f2.detected_at)
                FROM failure_atlas_entries f2
                WHERE f2.failure_type = f1.failure_type
                AND f2.detection_classification IN ({placeholders})
            )
            ORDER BY f1.detected_at DESC
            LIMIT 20
            """,
            (*classifications, *classifications),
        )
        return [row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# ====================================================
# SIMILAR FAILURES
# ====================================================

@app.get("/similar-failures/{failure_type}")
def get_similar_failures(
    failure_type: str,
    limit: int = Query(10, ge=1, le=50),
    include_heuristic: bool = Query(False),
    include_unverified: bool = Query(False),
):
    conn = get_connection()
    try:
        classifications = get_classification_filter(include_heuristic, include_unverified)
        placeholders = ",".join("?" for _ in classifications)

        cursor = conn.cursor()
        cursor.execute(
            f"""
            SELECT failure_type, fix_type,
                   COUNT(*) as sample_size,
                   ROUND(CAST(SUM(fix_applied) AS FLOAT) / COUNT(*) * 100, 1) as success_rate
            FROM failure_atlas_entries
            WHERE failure_type = ?
            AND detection_classification IN ({placeholders})
            GROUP BY failure_type, fix_type
            ORDER BY sample_size DESC
            LIMIT ?
            """,
            (failure_type, *classifications, limit),
        )
        results = [dict(row) for row in cursor.fetchall()]
        return {
            "failure_type": failure_type,
            "total_cases": sum(r.get("sample_size", 0) for r in results),
            "fix_strategies": results,
            "total": sum(r.get("sample_size", 0) for r in results),
            "results": results,
        }
    finally:
        conn.close()


# ====================================================
# RUN DIFF
# ====================================================

@app.get("/runs/{run_id}/diff/{previous_run_id}")
def get_run_diff(run_id: str, previous_run_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        current = cursor.fetchone()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (previous_run_id,))
        previous = cursor.fetchone()

        if not current or not previous:
            raise HTTPException(status_code=404, detail="Run not found")

        diff_fields = [
            "wns", "tns", "utilization", "runtime_sec",
            "cell_count", "qor_score",
        ]
        diffs = {}
        for field in diff_fields:
            curr_val = current[field] if field in current.keys() else None
            prev_val = previous[field] if field in previous.keys() else None
            if curr_val is not None and prev_val is not None:
                diffs[field] = {
                    "before": prev_val,
                    "after": curr_val,
                    "delta": round(curr_val - prev_val, 4),
                }
            elif curr_val is not None:
                diffs[field] = {"before": None, "after": curr_val, "delta": None}

        return {
            "run_id": run_id,
            "previous_run_id": previous_run_id,
            "diffs": diffs,
            "likely_regression": any(
                d.get("delta", 0) < 0 for d in diffs.values()
                if d.get("delta") is not None and isinstance(d["delta"], (int, float))
            ),
        }
    finally:
        conn.close()


@app.patch("/runs/{run_id}/important")
def toggle_important_run(run_id: str, payload: dict):
    is_important = payload.get("is_important", False)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE runs SET is_important = ?, important_marked_at = ? WHERE run_id = ?",
            (1 if is_important else 0, datetime.now().isoformat() if is_important else None, run_id),
        )
        conn.commit()

        # Telemetry collection
        from gli_flow.telemetry.manager import TelemetryManager
        
        # We need the output path for the run to instantiate TelemetryManager
        run_dir = _OUTPUTS_DIR / run_id
        if run_dir.is_dir():
            tm = TelemetryManager(str(run_dir))
            tm.export_stage_data("user_action", {
                "action": "important_run_marked",
                "is_important": is_important,
                "timestamp": datetime.now().isoformat()
            })
            
        return {"status": "ok", "is_important": is_important}
    finally:
        conn.close()


# ====================================================
# KNOWLEDGE BASE ENDPOINTS
# ====================================================

_knowledge_base = None


def load_knowledge_base():
    global _knowledge_base
    if _knowledge_base is not None:
        return _knowledge_base
    kb_path = Path(__file__).resolve().parent.parent / "failure_atlas" / "knowledge_base.json"
    if kb_path.exists():
        try:
            _knowledge_base = json.loads(kb_path.read_text())
        except Exception:
            _knowledge_base = {}
    else:
        _knowledge_base = {}
    return _knowledge_base


@app.get("/knowledge/failures")
def get_knowledge_failures():
    kb = load_knowledge_base()
    return {
        "entries": [
            {"failure_type": k, **v} for k, v in kb.items()
        ]
    }


@app.get("/knowledge/failures/{identifier}")
def get_knowledge_failure(identifier: str, citation: str = Query(None)):
    # Priority 1: Signature library lookup (exact rule_id match)
    signatures_dir = Path(__file__).resolve().parent.parent / "failure_atlas" / "signatures"
    for json_file in signatures_dir.rglob("*.json"):
        try:
            sig = json.loads(json_file.read_text())
            if sig.get("rule_id") == identifier:
                print(f"[TELEMETRY] rule_knowledge_viewed: rule_id={identifier}, source=signature_library")
                return {
                    "failure_type": identifier,
                    "description": sig.get("description"),
                    "remediation_strategies": [
                        {"technique": "Investigation", "description": step} for step in sig.get("investigation_checklist", [])
                    ],
                    "verification_steps": sig.get("known_causes", []),
                    "source": "signature_library",
                    "version": "v1",
                }
        except Exception:
            continue

    # Priority 2: Legacy knowledge base lookup by identifier
    kb = load_knowledge_base()
    normalized = identifier.upper().replace("-", "_").replace(" ", "_")
    for key, value in kb.items():
        if key.upper().replace("-", "_").replace(" ", "_") == normalized:
            print(f"[TELEMETRY] rule_knowledge_viewed: rule_id={identifier}, source=legacy_kb")
            return {"failure_type": key, **value, "source": "legacy_kb", "version": "v1"}

    # Priority 3: Citation-based lookup (evidence.citation fallback)
    if citation:
        normalized_citation = citation.upper().replace("-", "_").replace(" ", "_")
        for key, value in kb.items():
            if key.upper().replace("-", "_").replace(" ", "_") == normalized_citation:
                print(f"[TELEMETRY] rule_knowledge_viewed: rule_id={identifier}, citation={citation}, source=legacy_kb_citation")
                return {"failure_type": key, **value, "source": "legacy_kb", "version": "v1"}

        # Also try matching citation against each entry's "citation" field
        for key, value in kb.items():
            entry_citation = str(value.get("citation", "")).upper().replace("-", "_").replace(" ", "_")
            if entry_citation == normalized_citation:
                print(f"[TELEMETRY] rule_knowledge_viewed: rule_id={identifier}, citation={citation}, source=legacy_kb_field")
                return {"failure_type": key, **value, "source": "legacy_kb", "version": "v1"}

    # Telemetry: signature missing
    print(f"[TELEMETRY] failure_atlas_knowledge_lookup_failed: rule_id={identifier}, citation={citation}")
    raise HTTPException(status_code=404, detail="Failure type not found in knowledge base")


@app.get("/knowledge/search")
def search_knowledge(q: str = Query("", min_length=1)):
    kb = load_knowledge_base()
    results = []
    ql = q.lower()
    for key, value in kb.items():
        if ql in key.lower() or ql in str(value).lower():
            results.append({"failure_type": key, **value})
    return {"query": q, "results": results}


@app.get("/knowledge/qor")
def get_qor_playbook():
    qp_path = Path(__file__).resolve().parent.parent / "failure_atlas" / "qor_playbook.json"
    if qp_path.exists():
        try:
            return json.loads(qp_path.read_text())
        except Exception:
            pass
    return {}


# ====================================================
# RELIABILITY ENDPOINTS
# ====================================================

_RELIABILITY_BASE = Path(__file__).resolve().parent.parent / "outputs" / "reports"


@app.get("/reliability/summary")
def get_reliability_summary():
    reliability_file = _RELIABILITY_BASE / "reliability_report.json"
    health_file = _RELIABILITY_BASE / "execution_health_v3.json"

    scores = []
    if reliability_file.exists():
        try:
            scores = json.loads(reliability_file.read_text())
        except Exception:
            pass

    if not scores:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT run_id, status FROM runs ORDER BY timestamp DESC LIMIT 50")
            for row in cursor.fetchall():
                health = "HEALTHY" if row["status"] in ("SUCCESS", "COMPLETED") else ("FAILED" if row["status"] == "FAILED" else "WARNING")
                score = 90 if health == "HEALTHY" else (20 if health == "FAILED" else 60)
                confidence = "HIGH" if health == "HEALTHY" else ("LOW" if health == "FAILED" else "MEDIUM")
                scores.append({"run": row["run_id"], "status": row["status"], "health": health, "reliability_score": score, "confidence": confidence})
        finally:
            conn.close()

    if not scores:
        return {"total_runs": 0, "avg_score": 0, "health_distribution": {}, "confidence_distribution": {}, "scores": []}

    health_dist = {}
    confidence_dist = {}
    total_score = 0
    for s in scores:
        h = s.get("health", "UNKNOWN")
        health_dist[h] = health_dist.get(h, 0) + 1
        c = s.get("confidence", "UNKNOWN")
        confidence_dist[c] = confidence_dist.get(c, 0) + 1
        total_score += s.get("reliability_score", 0)

    return {
        "total_runs": len(scores),
        "avg_score": round(total_score / len(scores), 1) if scores else 0,
        "health_distribution": health_dist,
        "confidence_distribution": confidence_dist,
        "scores": scores,
    }


@app.get("/reliability/health")
def get_reliability_health():
    health_file = _RELIABILITY_BASE / "execution_health_v3.json"
    if health_file.exists():
        try:
            return json.loads(health_file.read_text())
        except Exception:
            pass

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT run_id, status, current_stage, progress FROM runs ORDER BY timestamp DESC LIMIT 50")
        results = []
        for row in cursor.fetchall():
            status = row["status"]
            health = "HEALTHY" if status in ("SUCCESS", "COMPLETED") else ("FAILED" if status == "FAILED" else "WARNING")
            results.append({"run": row["run_id"], "status": status, "health": health, "current_stage": row["current_stage"], "progress": row["progress"]})
        return results
    finally:
        conn.close()


@app.get("/reliability/trends")
def get_reliability_trends():
    trend_file = _RELIABILITY_BASE / "reliability_trend_report.json"
    if trend_file.exists():
        try:
            return json.loads(trend_file.read_text())
        except Exception:
            pass
    return {"message": "No trend data available", "trends": []}


# ====================================================
# PROVENANCE ENDPOINTS
# ====================================================

_PROVENANCE_DIR = Path(__file__).resolve().parent.parent / "provenance"


@app.get("/provenance/summary")
def get_provenance_summary():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM runs")
        total_runs = cursor.fetchone()[0]
        cursor.execute("SELECT run_id, design_name, status, qor_score, timestamp FROM runs ORDER BY timestamp DESC LIMIT 20")
        recent_runs = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    manifest_files = list(Path(__file__).resolve().parent.parent.glob("outputs/runs/*/reports/reproducibility.json"))
    manifest_count = len(manifest_files)

    provenance_graph = _PROVENANCE_DIR / "provenance_graph.json"
    graph = {}
    if provenance_graph.exists():
        try:
            graph = json.loads(provenance_graph.read_text())
        except Exception:
            pass

    return {
        "total_runs": total_runs,
        "runs_with_manifests": manifest_count,
        "graph_nodes": len(graph.get("nodes", [])),
        "graph_edges": len(graph.get("edges", [])),
        "recent_runs": recent_runs,
    }


@app.get("/provenance/manifests")
def get_provenance_manifests():
    manifests = []
    for m_file in sorted(Path(__file__).resolve().parent.parent.glob("outputs/runs/*/reports/reproducibility.json"), reverse=True)[:20]:
        try:
            manifests.append(json.loads(m_file.read_text()))
        except Exception:
            pass

    if not manifests:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT run_id, design_name, status, qor_score, timestamp FROM runs ORDER BY timestamp DESC LIMIT 20")
            for row in cursor.fetchall():
                manifests.append({
                    "manifest_version": "2.0",
                    "run_id": row["run_id"],
                    "design_name": row["design_name"],
                    "timestamp_iso": row["timestamp"] if row["timestamp"] else "",
                    "system": {
                        "platform": "inferred",
                        "python_version": "derived",
                        "hostname": "dashboard",
                    },
                    "toolchain": {
                        "openroad": "inferred",
                        "yosys": "inferred",
                        "python": "inferred",
                    },
                    "provenance": {
                        "rtl_hashes": {},
                        "pdk": {"name": "inferred", "root": ""},
                    },
                    "execution": {
                        "reproduction_command": f"gli-flow run {row['design_name']}",
                        "reproducibility_mode": True,
                    },
                    "metrics": {"qor_score": row["qor_score"]},
                    "status": row["status"],
                })
        finally:
            conn.close()

    return manifests


@app.get("/provenance/graph")
def get_provenance_graph():
    provenance_graph = _PROVENANCE_DIR / "provenance_graph.json"
    if provenance_graph.exists():
        try:
            return json.loads(provenance_graph.read_text())
        except Exception:
            pass

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT run_id, design_name, status FROM runs ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
    finally:
        conn.close()

    nodes = []
    edges = []
    for row in rows:
        nodes.append({"id": row["run_id"], "name": row["run_id"], "type": "run", "design": row["design_name"], "status": row["status"]})
    if len(nodes) >= 2:
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i + 1]["id"], "relation": "precedes"})

    return {"nodes": nodes, "edges": edges}


from failure_atlas.correlation_engine import get_correlation_data
from failure_atlas.coverage_engine import get_coverage_data
from failure_atlas.repository import FailureAtlasRepository
from failure_atlas.ai_assistant import (
    should_use_ai, build_context, AIResponse, validate_response,
    FeedbackStore, ResolutionCapture,
)


@app.get("/failures/{failure_id}/run")
def get_failure_run_id(failure_id: str):
    """Resolve a failure ID to its associated run_id.
    Bridge for Failure Atlas → InvestigationLayer integration.
    """
    repo = FailureAtlasRepository()
    try:
        entry = repo.get_failure_by_id(failure_id) if failure_id else None
        if entry and entry.get("run_id"):
            return {"run_id": entry["run_id"]}

        entries = repo.search_entries(limit=1, offset=0)
        if entries and entries[0].get("run_id"):
            return {"run_id": entries[0]["run_id"], "note": "fallback to most recent occurrence"}

        return {"run_id": None, "detail": "No associated run found for this failure"}
    finally:
        repo.close()


@app.get("/failure-atlas")
def get_failure_atlas_incidents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    severity: str = Query(None),
    failure_type: str = Query(None),
):
    repo = FailureAtlasRepository()
    try:
        entries = repo.search_entries(
            severity=severity,
            failure_type=failure_type,
            limit=limit,
            offset=offset,
        )
        total = repo.count_entries(failure_type=failure_type)
        return {"total": total, "limit": limit, "offset": offset, "results": entries}
    finally:
        repo.close()

@app.get("/failures/correlation/{failure_type}")
def get_failure_correlation(failure_type: str):
    return get_correlation_data(failure_type)

@app.get("/analytics/coverage")
def get_coverage_analytics():
    return get_coverage_data()

@app.get("/telemetry/events")
def list_telemetry_events(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List telemetry events from community_telemetry."""
    from failure_atlas.community_intelligence import EscalationTelemetry
    telemetry = EscalationTelemetry()
    events = telemetry.get_events(limit=limit, offset=offset)
    total = telemetry.get_event_count()
    return {"results": events, "total": total}


@app.post("/telemetry/event")
def record_event(payload: dict):
    """Persist telemetry events to community_telemetry.

    Validates payload, classifies event, records to database.
    Never stores RTL, netlists, GDS, DEF, LEF, or source code.
    """
    import logging
    log = logging.getLogger(__name__)

    event = payload.get("event", "")
    if not event:
        raise HTTPException(status_code=400, detail="event field is required")

    allowed_events = {
        "escalation_created", "escalation_sent", "escalation_resolved",
        "knowledge_created", "signature_created",
        "unknown_failure_detected", "ai_investigation_run",
        "failure_atlas_miss", "dashboard_view",
    }
    if event not in allowed_events:
        log.warning(f"Ignoring unrecognized telemetry event: {event}")
        return {"status": "ok", "warning": "unrecognized event type"}

    details = payload.get("details", {}) or {}
    safe_keys = {"signature", "error_class", "confidence", "severity",
                  "stage", "tool", "failure_type", "frequency",
                  "ai_helpfulness", "resolution_outcome"}
    sanitized = {k: v for k, v in details.items() if k in safe_keys}

    from failure_atlas.community_intelligence import EscalationTelemetry
    telemetry = EscalationTelemetry()
    try:
        telemetry.record(
            event=event,
            escalation_id=payload.get("escalation_id", ""),
            failure_type=payload.get("failure_type", ""),
            tool=payload.get("tool", ""),
            atlas_id=payload.get("atlas_id", ""),
            details=sanitized,
        )
        log.info(f"Telemetry recorded: event={event}")
    except Exception as e:
        log.error(f"Telemetry ingestion failed: {e}")
        raise HTTPException(status_code=500, detail="Telemetry ingestion failed — check server logs for details")

    return {"status": "ok"}


@app.get("/telemetry/export")
def export_telemetry(
    run_id: str = Query(""),
    from_date: str = Query(""),
    to_date: str = Query(""),
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """Export sanitized telemetry data."""
    from failure_atlas.community_intelligence.export import TelemetryExporter
    exporter = TelemetryExporter()
    fmt = format.lower()
    if fmt == "csv":
        outputs = exporter.export_to_csv(
            run_id=run_id or None,
            from_date=from_date or None,
            to_date=to_date or None,
        )
        return {"status": "ok", "format": "csv", "sections": outputs}
    data = exporter.export_to_json(
        run_id=run_id or None,
        from_date=from_date or None,
        to_date=to_date or None,
    )
    return JSONResponse(content=json.loads(data))


@app.get("/telemetry/health")
def get_telemetry_health():
    """Get telemetry pipeline health status."""
    from failure_atlas.community_intelligence.health import TelemetryHealth
    health = TelemetryHealth()
    return health.get_health()


@app.get("/telemetry/audit-log")
def get_telemetry_audit_log(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    event_type: str = Query(""),
):
    """Get telemetry audit log entries."""
    from failure_atlas.community_intelligence.audit import TelemetryAuditLog
    audit = TelemetryAuditLog()
    logs = audit.get_logs(
        limit=limit, offset=offset,
        event_type=event_type or None,
    )
    stats = audit.get_stats()
    return {"results": logs, "stats": stats}


@app.post("/telemetry/replay")
def replay_telemetry(payload: dict):
    """Replay telemetry events from an export payload."""
    from failure_atlas.community_intelligence.replay import TelemetryReplayEngine
    engine = TelemetryReplayEngine()
    dry_run = payload.get("dry_run", True)
    filepath = payload.get("filepath", "")
    if not filepath and "data" not in payload:
        raise HTTPException(status_code=400, detail="Provide filepath or data")
    if filepath:
        results = engine.replay(filepath, dry_run=dry_run)
    else:
        data = payload["data"]
        import tempfile
        import json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            tmp_path = f.name
        try:
            results = engine.replay(tmp_path, dry_run=dry_run)
        finally:
            import os
            os.unlink(tmp_path)
    return results


@app.post("/telemetry/snapshot")
def create_telemetry_snapshot(payload: dict = {}):
    """Create a dataset snapshot for AI training preparation."""
    from failure_atlas.community_intelligence.snapshot import DatasetSnapshot
    output_path = payload.get("output_path", "")
    snapshot = DatasetSnapshot()
    result = snapshot.create(output_path=output_path or None)
    return result


@app.get("/telemetry/privacy-validate")
def validate_telemetry_privacy():
    """Run privacy validation against all telemetry data."""
    from failure_atlas.community_intelligence.export import TelemetryExporter
    exporter = TelemetryExporter()
    data = exporter.export_telemetry()
    report = data.get("export_metadata", {}).get("privacy_report", {})
    return report


# ====================================================
# AI INVESTIGATION ASSISTANT ENDPOINTS
# ====================================================


@app.get("/ai/health")
def ai_health():
    """Health check for AI investigation availability.

    Returns detailed status of all pre-flight checks:
    - enabled
    - provider
    - api_key_present
    - api_key_valid
    - model_configured
    - provider_reachable
    - status (READY, UNAVAILABLE, INVALID_CONFIGURATION, MISCONFIGURED)
    - reason (human-readable explanation if not READY)
    - fix (how to resolve the issue)
    """
    result = _ai_availability_service.check_availability()
    return {
        "enabled": result.enabled,
        "provider": result.provider,
        "api_key_present": result.api_key_present,
        "api_key_valid": result.api_key_valid,
        "model_configured": result.model_configured,
        "provider_reachable": result.provider_reachable,
        "status": result.status,
        "reason": result.reason,
        "fix": result.fix,
    }


@app.get("/ai/trigger")
def get_ai_trigger(
    failure_type: str = Query(""),
    signature: str = Query(""),
    severity: str = Query("MEDIUM"),
    confidence: float = Query(0.0),
    run_id: str = Query(""),
):
    trigger = should_use_ai(
        failure_type=failure_type,
        signature=signature,
        severity=severity,
        confidence=confidence,
        run_id=run_id or None,
    )
    return dataclasses.asdict(trigger)


@app.post("/ai/investigate")
def ai_investigate(payload: dict):
    """Generate AI investigation guidance for a failure.

    The endpoint:
    1. Checks trigger conditions
    2. Builds context package
    3. Returns heuristic fallback guidance
    (Future: plug in LLM provider)
    """
    failure_type = payload.get("failure_type", "UNKNOWN")
    signature = payload.get("signature", "")
    severity = payload.get("severity", "MEDIUM")
    confidence = payload.get("confidence", 0.0)
    tool = payload.get("tool", "")
    stage = payload.get("stage", "")
    error_text = payload.get("error_text", "")
    log_snippet = payload.get("log_snippet", "")
    metrics = payload.get("metrics", {})
    design_metadata = payload.get("design_metadata", {})
    run_metadata = payload.get("run_metadata", {})
    known_evidence = payload.get("known_evidence", {})

    trigger = should_use_ai(
        failure_type=failure_type,
        signature=signature,
        severity=severity,
        confidence=confidence,
    )

    if trigger.use_ai:
        _capture_unknown_failure(
            tool=tool,
            failure_type=failure_type,
            signature=signature,
            severity=severity,
            confidence=confidence,
            stage=stage,
            source="ai_investigate",
        )

    context = build_context(
        tool=tool,
        stage=stage,
        error_text=error_text,
        log_snippet=log_snippet,
        failure_type=failure_type,
        metrics=metrics,
        design_metadata=design_metadata,
        run_metadata=run_metadata,
        known_evidence=known_evidence,
    )

    response = AIResponse.heuristic_fallback(context.to_dict())
    errors = validate_response(response.to_dict())

    return {
        "trigger": dataclasses.asdict(trigger),
        "context": context.to_dict(),
        "response": response.to_dict(),
        "validation_errors": errors,
    }


@app.get("/ai/investigate/failure")
def ai_investigate_failure(
    failure_id: str = Query(""),
    run_id: str = Query(""),
):
    """Investigate a specific failure from the database."""
    repo = FailureAtlasRepository()
    try:
        entry = repo.get_failure_by_id(failure_id) if failure_id else None
        if not entry and run_id:
            entries = repo.get_failures_for_run(run_id)
            if entries:
                entry = entries[0]

        if not entry:
            raise HTTPException(status_code=404, detail="Failure not found")

        ev = {}
        if isinstance(entry.get("evidence"), str):
            try:
                ev = json.loads(entry["evidence"])
            except (json.JSONDecodeError, TypeError):
                pass
        elif isinstance(entry.get("evidence"), dict):
            ev = entry["evidence"]

        failure_type = entry.get("failure_type", "UNKNOWN")
        signature = entry.get("signature", "")
        severity = entry.get("severity", "MEDIUM")
        confidence = entry.get("confidence", 0.0)

        trigger = should_use_ai(
            failure_type=failure_type,
            signature=signature,
            severity=severity,
            confidence=confidence,
            run_id=run_id or entry.get("run_id"),
            repo=repo,
        )

        if trigger.use_ai:
            _capture_unknown_failure(
                tool=ev.get("tool", entry.get("tool_name", "")),
                failure_type=failure_type,
                signature=signature,
                severity=severity,
                confidence=confidence,
                stage=ev.get("stage", entry.get("tool_stage", "")),
                source="ai_investigate_failure",
                run_id=run_id or entry.get("run_id"),
            )

        context = build_context(
            tool=ev.get("tool", entry.get("tool_name", "")),
            stage=ev.get("stage", entry.get("tool_stage", "")),
            error_text=entry.get("description", ""),
            failure_type=failure_type,
            metrics=ev.get("metrics", {}),
            known_evidence=ev,
        )

        response = AIResponse.heuristic_fallback(context.to_dict())
        errors = validate_response(response.to_dict())

        return {
            "failure": entry,
            "trigger": dataclasses.asdict(trigger),
            "context": context.to_dict(),
            "response": response.to_dict(),
            "validation_errors": errors,
        }
    finally:
        repo.close()


@app.post("/ai/feedback")
def record_ai_feedback(payload: dict):
    """Record user feedback on AI investigation guidance."""
    investigation_id = payload.get("investigation_id", "")
    feedback_type = payload.get("feedback_type", "")
    resolved = payload.get("resolved", False)
    comment = payload.get("comment", "")
    run_id = payload.get("run_id", "")
    failure_type = payload.get("failure_type", "")

    if not investigation_id or not feedback_type:
        raise HTTPException(status_code=400, detail="investigation_id and feedback_type are required")

    allowed = {"helpful", "not_helpful", "resolved", "did_not_resolve"}
    if feedback_type not in allowed:
        raise HTTPException(status_code=400, detail=f"feedback_type must be one of {allowed}")

    store = FeedbackStore()
    try:
        entry_id = store.record_feedback(
            investigation_id=investigation_id,
            feedback_type=feedback_type,
            resolved=resolved,
            comment=comment,
            run_id=run_id,
            failure_type=failure_type,
        )
        return {"status": "ok", "feedback_id": entry_id}
    finally:
        pass


@app.get("/ai/feedback/{investigation_id}")
def get_ai_feedback(investigation_id: str):
    store = FeedbackStore()
    try:
        return store.get_feedback_for_investigation(investigation_id)
    finally:
        pass


@app.get("/ai/feedback-summary")
def get_ai_feedback_summary(failure_type: str = Query("")):
    store = FeedbackStore()
    try:
        return store.get_feedback_summary(failure_type=failure_type or None)
    finally:
        pass


@app.post("/ai/resolution")
def record_ai_resolution(payload: dict):
    """Capture a resolution that was guided by the AI assistant."""
    investigation_id = payload.get("investigation_id", "")
    failure_type = payload.get("failure_type", "")
    tool = payload.get("tool", "")
    fix_description = payload.get("fix_description", "")
    resolution_outcome = payload.get("resolution_outcome", "")
    stage = payload.get("stage", "")
    design_name = payload.get("design_name", "")
    pdk = payload.get("pdk", "")
    metrics_before = payload.get("metrics_before", {})
    metrics_after = payload.get("metrics_after", {})

    if not investigation_id or not failure_type or not fix_description:
        raise HTTPException(status_code=400, detail="investigation_id, failure_type, and fix_description are required")

    capture = ResolutionCapture()
    try:
        entry_id = capture.record_resolution(
            investigation_id=investigation_id,
            failure_type=failure_type,
            tool=tool,
            fix_description=fix_description,
            resolution_outcome=resolution_outcome,
            stage=stage,
            design_name=design_name,
            pdk=pdk,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
        )
        return {"status": "ok", "capture_id": entry_id}
    finally:
        pass


@app.get("/ai/resolutions")
def get_ai_resolutions(failure_type: str = Query(""), limit: int = Query(20, ge=1, le=100)):
    capture = ResolutionCapture()
    try:
        return {
            "results": capture.get_captured_resolutions(
                failure_type=failure_type or None,
                limit=limit,
            ),
            "total": capture.get_resolution_count(),
        }
    finally:
        pass


# ── Pipeline Helpers ──

def _capture_unknown_failure(
    tool: str,
    failure_type: str,
    signature: str = "",
    severity: str = "MEDIUM",
    confidence: float = 0.0,
    stage: str = "",
    source: str = "unknown",
    run_id: str = "",
):
    """Auto-capture an unknown failure into dataset + telemetry.

    Called when the Failure Atlas cannot classify a failure
    (use_ai=True from should_use_ai). Does NOT store RTL, GDS,
    netlists, DEF, LEF, or source code — only signatures/metadata.
    """
    import logging
    _log = logging.getLogger(__name__)

    from failure_atlas.community_intelligence import (
        EscalationTelemetry,
        UnknownFailureDataset,
    )

    try:
        dataset = UnknownFailureDataset()
        dataset.record_unknown_failure(
            tool=tool,
            failure_type=failure_type,
            signature=signature,
        )
    except Exception as e:
        _log.warning(f"Unknown failure dataset capture failed: {e}")

    try:
        telemetry = EscalationTelemetry()
        telemetry.record(
            event="failure_atlas_miss",
            failure_type=failure_type,
            tool=tool,
            details={
                "signature": signature,
                "severity": severity,
                "confidence": confidence,
                "stage": stage,
                "source": source,
                "error_class": failure_type,
            },
        )
        _log.info(
            f"Unknown failure captured: tool={tool} "
            f"failure_type={failure_type} source={source}"
        )
    except Exception as e:
        _log.warning(f"Telemetry record failed for unknown failure: {e}")


# ── Resolution Intelligence API ─────────────────────────────────────────

def _get_resolution_repo():
    conn = get_connection()
    return ResolutionRepository(conn), conn


@app.get("/resolutions/patterns")
def list_resolution_patterns(
    failure_type: str = Query(""),
    fingerprint: str = Query(""),
    limit: int = Query(20, ge=1, le=100),
):
    """List resolution patterns, optionally filtered by failure_type or fingerprint."""
    repo, conn = _get_resolution_repo()
    try:
        if fingerprint:
            patterns = repo.find_by_fingerprint(fingerprint)
        elif failure_type:
            patterns = repo.find_by_failure_type(failure_type, limit)
        else:
            patterns = repo.get_top_resolved(limit)
        return {
            "patterns": [
                {
                    "id": p.id,
                    "failure_fingerprint": p.failure_fingerprint,
                    "failure_type": p.failure_type,
                    "root_cause": p.root_cause,
                    "resolution": p.resolution,
                    "resolution_type": p.resolution_type,
                    "success_count": p.success_count,
                    "failure_count": p.failure_count,
                    "confidence": p.confidence,
                    "total_attempts": p.total_attempts,
                    "first_seen": p.first_seen,
                    "last_seen": p.last_seen,
                    "trust_score": p.trust_score,
                    "trust_level": p.trust_level,
                    "trust_reason": p.trust_reason,
                    "unique_runs": p.unique_runs,
                    "unique_designs": p.unique_designs,
                    "engineer_confirmations": p.engineer_confirmations,
                    "contradictory_reports": p.contradictory_reports,
                }
                for p in patterns
            ],
            "total": len(patterns),
        }
    finally:
        conn.close()


@app.get("/resolutions/patterns/{fingerprint}/timeline")
def get_resolution_timeline(fingerprint: str):
    """Get resolution timeline for a failure fingerprint."""
    repo, conn = _get_resolution_repo()
    try:
        timeline = repo.get_timeline(fingerprint)
        return {"fingerprint": fingerprint, "timeline": timeline}
    finally:
        conn.close()


@app.post("/resolutions/capture")
def capture_resolution(payload: dict):
    """Record a potential fix relationship when a run recovers.

    Expects:
        failed_run_id, successful_run_id, failure_fingerprint,
        failure_type, resolution
    """
    capture = ResolutionCapture(get_connection())
    try:
        pattern_id = capture.capture_from_run_recovery(
            failed_run_id=payload.get("failed_run_id", ""),
            successful_run_id=payload.get("successful_run_id", ""),
            failure_fingerprint=payload.get("failure_fingerprint", ""),
            failure_type=payload.get("failure_type", ""),
            resolution=payload.get("resolution", ""),
            resolution_type=payload.get("resolution_type"),
            root_cause=payload.get("root_cause"),
        )
        return {"status": "ok", "pattern_id": pattern_id}
    finally:
        pass


@app.post("/resolutions/feedback")
def record_resolution_feedback(payload: dict):
    """Record user feedback on a resolution.

    Body: { pattern_id, run_id, feedback_type: "confirmed" | "rejected" }
    """
    pattern_id = payload.get("pattern_id", "")
    run_id = payload.get("run_id", "")
    feedback_type = payload.get("feedback_type", "")

    if not pattern_id or not feedback_type:
        raise HTTPException(status_code=400, detail="pattern_id and feedback_type are required")
    if feedback_type not in ("confirmed", "rejected"):
        raise HTTPException(status_code=400, detail="feedback_type must be 'confirmed' or 'rejected'")

    repo, conn = _get_resolution_repo()
    try:
        feedback_id = repo.record_feedback(pattern_id, run_id, feedback_type)
        return {"status": "ok", "feedback_id": feedback_id}
    finally:
        conn.close()


@app.get("/resolutions/summary")
def get_resolution_summary():
    """Get summary statistics for resolution patterns."""
    repo, conn = _get_resolution_repo()
    try:
        return repo.get_summary_stats()
    finally:
        conn.close()


@app.get("/resolutions/trust-summary")
def get_resolution_trust_summary():
    """Get trust score distribution across all resolution patterns."""
    repo, conn = _get_resolution_repo()
    try:
        return repo.get_trust_summary()
    finally:
        conn.close()


@app.get("/resolutions/candidates")
def get_resolution_candidates(
    min_confidence: float = Query(0.75, ge=0.0, le=1.0),
    min_occurrences: int = Query(3, ge=1),
):
    """Get resolution candidates ready for Failure Atlas promotion."""
    generator = AtlasCandidateGenerator(get_connection())
    try:
        candidates = generator.generate_candidates(
            min_confidence=min_confidence,
            min_occurrences=min_occurrences,
        )
        return {"candidates": candidates, "total": len(candidates)}
    finally:
        pass


@app.post("/resolutions/promote")
def promote_resolution(payload: dict):
    """Promote a resolution candidate to the Failure Atlas (engineer review required).

    Body: { failure_fingerprint, failure_type, resolution, confidence,
            occurrence_count, first_seen, last_seen, reviewer_notes }
    """
    reviewer_notes = payload.get("reviewer_notes", "")
    generator = AtlasCandidateGenerator(get_connection())
    try:
        entry_id = generator.promote_to_atlas(payload, reviewer_notes=reviewer_notes)
        return {"status": "ok", "atlas_entry_id": entry_id}
    finally:
        pass


@app.get("/runs/{run_id}/compare/{other_run_id}")
def compare_runs(run_id: str, other_run_id: str):
    """Compare two runs to identify what changed."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        run_a = cursor.fetchone()
        cursor.execute("SELECT * FROM runs WHERE run_id = ?", (other_run_id,))
        run_b = cursor.fetchone()
        if not run_a or not run_b:
            missing = run_id if not run_a else other_run_id
            raise HTTPException(status_code=404, detail=f"Run {missing} not found")

        engine = RunComparisonEngine()
        comparison = engine.compare(dict(run_a), dict(run_b))

        cursor.execute(
            "SELECT * FROM failure_atlas_entries WHERE run_id = ?",
            (run_id,),
        )
        failures_a = [dict(r) for r in cursor.fetchall()]
        cursor.execute(
            "SELECT * FROM failure_atlas_entries WHERE run_id = ?",
            (other_run_id,),
        )
        failures_b = [dict(r) for r in cursor.fetchall()]

        comparison = engine.compare_with_failures(
            dict(run_a), dict(run_b), failures_a, failures_b,
        )

        return {
            "run_a": {"run_id": run_id, "status": run_a["status"]},
            "run_b": {"run_id": other_run_id, "status": run_b["status"]},
            "fields": comparison.fields,
            "qor_changes": comparison.qor_changes,
            "failure_diffs": comparison.failure_diffs,
        }
    finally:
        conn.close()


@app.get("/resolutions/top-resolved")
def get_top_resolved(limit: int = Query(10, ge=1, le=50)):
    """Get top resolved failure types by confidence."""
    repo, conn = _get_resolution_repo()
    try:
        patterns = repo.get_top_resolved(limit)
        return {
            "patterns": [
                {
                    "failure_type": p.failure_type,
                    "resolution": p.resolution,
                    "confidence": p.confidence,
                    "success_count": p.success_count,
                    "total_attempts": p.total_attempts,
                    "trust_score": p.trust_score,
                    "trust_level": p.trust_level,
                    "trust_reason": p.trust_reason,
                }
                for p in patterns
            ],
            "total": len(patterns),
        }
    finally:
        conn.close()


@app.get("/resolutions/top-unresolved")
def get_top_unresolved(limit: int = Query(10, ge=1, le=50)):
    """Get top unresolved failure types (attempted but never succeeded)."""
    repo, conn = _get_resolution_repo()
    try:
        patterns = repo.get_top_unresolved(limit)
        return {
            "patterns": [
                {
                    "failure_type": p.failure_type,
                    "resolution": p.resolution,
                    "failure_count": p.failure_count,
                    "total_attempts": p.total_attempts,
                    "trust_score": p.trust_score,
                    "trust_level": p.trust_level,
                    "trust_reason": p.trust_reason,
                }
                for p in patterns
            ],
            "total": len(patterns),
        }
    finally:
        conn.close()


# ── Community Intelligence API ─────────────────────────────────────────────

@app.post("/community/escalate")
def create_community_escalation(payload: dict):
    """Create and submit a community escalation."""
    from failure_atlas.community_intelligence import EscalationManager, FailurePackageBuilder

    failure_type = payload.get("failure_type", "UNKNOWN")
    tool = payload.get("tool", "")
    stage = payload.get("stage", "")
    run_id = payload.get("run_id", "")
    user_notes = payload.get("notes", "")
    consent_given = payload.get("consent", False)
    error_text = payload.get("error_text", "")

    if not consent_given:
        raise HTTPException(status_code=400, detail="Consent is required to escalate")

    builder = FailurePackageBuilder(
        failure_type=failure_type,
        tool=tool,
        stage=stage,
        error_text=error_text,
    )
    pkg = builder.build()

    mgr = EscalationManager()
    try:
        escalation_id = mgr.create_escalation(
            run_id=run_id,
            failure_type=failure_type,
            tool=tool,
            stage=stage,
            user_notes=user_notes,
            consent_given=consent_given,
        )

        # Phase 3: Record telemetry event for escalation
        from failure_atlas.community_intelligence import EscalationTelemetry, UnknownFailureDataset
        import logging
        _log = logging.getLogger(__name__)
        try:
            telemetry = EscalationTelemetry()
            telemetry.record(
                event="escalation_created",
                escalation_id=escalation_id,
                failure_type=failure_type,
                tool=tool,
                details={"stage": stage, "consent_given": consent_given},
            )
        except Exception as e:
            _log.warning(f"Failed to record escalation telemetry: {e}")

        # Phase 2: Record in unknown failure dataset
        try:
            dataset = UnknownFailureDataset()
            dataset.record_unknown_failure(
                tool=tool,
                failure_type=failure_type,
                consent_given=consent_given,
                escalation_id=escalation_id,
            )
        except Exception as e:
            _log.warning(f"Failed to record unknown failure: {e}")

        return {
            "id": escalation_id,
            "status": "created",
            "failure_type": failure_type,
            "tool": tool,
            "stage": stage,
            "consent_given": consent_given,
            "created_at": datetime.now().isoformat(),
        }
    finally:
        mgr.close()


@app.get("/community/escalations")
def get_community_escalations(
    status: str = Query(""),
    limit: int = Query(50, ge=1, le=200),
):
    """List community escalations."""
    from failure_atlas.community_intelligence import EscalationManager
    mgr = EscalationManager()
    try:
        records = mgr.list_escalations(status=status or None, limit=limit)
        return {"results": records, "total": len(records)}
    finally:
        mgr.close()


@app.get("/community/escalation/{escalation_id}")
def get_community_escalation(escalation_id: str):
    """Get a specific escalation."""
    from failure_atlas.community_intelligence import EscalationManager
    mgr = EscalationManager()
    try:
        record = mgr.get_escalation(escalation_id)
        if not record:
            raise HTTPException(status_code=404, detail="Escalation not found")
        return record.to_dict() if hasattr(record, "to_dict") else {
            "id": record.id,
            "failure_type": record.failure_type,
            "tool": record.tool,
            "stage": record.stage,
            "status": record.status,
            "consent_given": record.consent_given,
            "user_notes": record.user_notes,
            "engineer_response": record.engineer_response,
            "bharatcode_submission_id": record.bharatcode_submission_id,
            "created_at": record.created_at,
            "sent_at": record.sent_at,
            "resolved_at": record.resolved_at,
        }
    finally:
        mgr.close()


@app.post("/community/escalation/{escalation_id}/response")
def record_community_response(escalation_id: str, payload: dict):
    """Record an engineer response for an escalation."""
    from failure_atlas.community_intelligence import EscalationManager
    mgr = EscalationManager()
    try:
        success = mgr.record_engineer_response(
            escalation_id=escalation_id,
            response_data=payload.get("response", {}),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Escalation not found")
        return {"status": "ok", "escalation_id": escalation_id}
    finally:
        mgr.close()


@app.get("/community/stats")
def get_community_stats():
    """Get community intelligence statistics."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM community_escalations")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM community_escalations WHERE status='open'")
        open_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM community_escalations WHERE engineer_response != '{}' AND engineer_response != ''")
        responded = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM community_telemetry")
        telemetry_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM community_unknown_dataset")
        dataset_count = cursor.fetchone()[0]

        cursor.execute("SELECT failure_type, frequency FROM community_unknown_dataset ORDER BY frequency DESC LIMIT 5")
        top_unknowns = [{"failure_type": r[0], "frequency": r[1]} for r in cursor.fetchall()]

        return {
            "total_escalations": total,
            "open_escalations": open_count,
            "responded_escalations": responded,
            "telemetry_events": telemetry_count,
            "dataset_entries": dataset_count,
            "top_unknown_failures": top_unknowns,
        }
    finally:
        conn.close()


@app.get("/community/unknown-dataset")
def get_community_unknown_dataset(
    limit: int = Query(50, ge=1, le=200),
    min_frequency: int = Query(1, ge=1),
):
    """Alias for /community/dataset — list unknown failure dataset entries."""
    return get_community_dataset(limit=limit, min_frequency=min_frequency)


@app.get("/community/dataset")
def get_community_dataset(
    limit: int = Query(50, ge=1, le=200),
    min_frequency: int = Query(1, ge=1),
):
    """Get unknown failure dataset entries."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tool, failure_type, signature, frequency, ai_helpfulness, resolution_outcome, last_seen "
            "FROM community_unknown_dataset WHERE frequency >= ? ORDER BY frequency DESC LIMIT ?",
            (min_frequency, limit),
        )
        rows = cursor.fetchall()
        results = [
            {
                "tool": r[0],
                "failure_type": r[1],
                "signature": r[2],
                "frequency": r[3],
                "ai_helpfulness": r[4],
                "resolution_outcome": r[5],
                "last_seen": r[6],
            }
            for r in rows
        ]
        return {"results": results, "total": len(results)}
    finally:
        conn.close()


@app.get("/community/knowledge-gaps")
def get_community_knowledge_gaps(limit: int = Query(20, ge=1, le=100)):
    """Identify knowledge gaps: high-frequency failures with no resolved outcome."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tool, failure_type, signature, frequency, ai_helpfulness
            FROM community_unknown_dataset
            WHERE resolution_outcome = '' OR resolution_outcome IS NULL
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        results = [
            {
                "tool": r[0],
                "failure_type": r[1],
                "signature": r[2],
                "frequency": r[3],
                "ai_helpfulness": r[4],
            }
            for r in rows
        ]
        return {"gaps": results, "total": len(results)}
    finally:
        conn.close()


@app.get("/runs/{run_id}/investigation")
def get_run_investigation(run_id: str):
    """Get the investigation result for a run, including history and failed attempts."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT llm_investigation_available, llm_investigation_status,
               llm_investigation_summary, llm_investigation_timestamp,
               llm_investigation_failed_attempts
               FROM runs WHERE run_id = ?""",
            (run_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Run not found")

        result = {
            "available": bool(row[0]),
            "status": row[1],
            "summary": row[2],
            "timestamp": row[3],
        }

        try:
            if row[4]:
                failed = json.loads(row[4])
                result["failed_attempts"] = failed.get("attempts", [])
            else:
                result["failed_attempts"] = []
        except (json.JSONDecodeError, TypeError):
            result["failed_attempts"] = []

        run_dir = _OUTPUTS_DIR / run_id
        investigation_path = run_dir / "investigation.json"
        if investigation_path.exists():
            try:
                raw = json.loads(investigation_path.read_text())
                result["investigation"] = raw.get("investigation", raw)
                result["file_status"] = raw.get("status")
            except (json.JSONDecodeError, OSError):
                pass

        from gli_flow.investigation.investigator import InvestigationLayer
        layer = InvestigationLayer(run_dir=str(run_dir), run_id=run_id)
        result["history"] = layer.get_investigation_history()
        result["has_backup"] = layer._backup_path().exists()
        return result
    finally:
        conn.close()


@app.post("/runs/{run_id}/investigation")
def trigger_run_investigation(run_id: str):
    """Trigger an LLM investigation for a run.

    Builds compact context, calls BharatCode, validates output,
    saves investigation.json, and updates the database.

    Hardened: preserves existing successful investigations on failure,
    maintains history, creates backups, validates API key before attempting.
    Uses InvestigationAvailabilityService as single source of truth.
    """
    availability = _ai_availability_service.check_availability()
    if not availability.is_ready:
        raise HTTPException(
            status_code=503 if availability.status == "UNAVAILABLE" else 400,
            detail=f"Investigation unavailable: {availability.reason}. Fix: {availability.fix}",
        )

    from gli_flow.investigation import InvestigationLayer

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT run_dir FROM runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Run not found")
        run_dir = row[0]
        if not run_dir or not Path(run_dir).exists():
            run_dir = str(_OUTPUTS_DIR / run_id)
        if not Path(run_dir).exists():
            raise HTTPException(status_code=400, detail="Run directory not found")
    finally:
        conn.close()

    layer = InvestigationLayer(run_dir=run_dir, run_id=run_id)

    result = layer.investigate()
    saved_path = layer.save_investigation(result)

    summary = ""
    if result.payload and result.payload.get("summary"):
        summary = result.payload["summary"]

    failed_attempts_json = None
    if not result.is_success():
        failed_attempts = layer.get_failed_attempts()
        failed_attempts_json = json.dumps({"attempts": failed_attempts})

    db = DatabaseManager()
    try:
        db.update_run_investigation(
            run_id=run_id,
            available=result.is_success(),
            status=result.status,
            summary=summary,
            timestamp=datetime.now().isoformat(),
            failed_attempts=failed_attempts_json,
        )
    finally:
        db.close()

    return {
        "status": result.status,
        "provider": result.provider,
        "model": result.model,
        "latency_sec": result.latency_sec,
        "error": result.error,
        "investigation": result.payload,
        "preserved_existing": not result.is_success() and layer.has_successful_investigation(),
    }


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Feedback Center (Phase 1)
# ═══════════════════════════════════════════════════════════════


@app.get("/feedback")
def list_feedback(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    feedback_type: str = Query(None),
    status: str = Query(None),
):
    conn = get_connection()
    try:
        conditions = []
        params = []
        if feedback_type:
            conditions.append("feedback_type = ?")
            params.append(feedback_type)
        if status:
            conditions.append("status = ?")
            params.append(status)
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM feedback_records WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        )
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.execute(f"SELECT COUNT(*) FROM feedback_records WHERE {where}", params)
        total = cursor.fetchone()[0]
        return {"total": total, "results": results}
    finally:
        conn.close()


@app.post("/feedback")
def submit_feedback(payload: dict):
    import uuid
    feedback_type = payload.get("feedback_type", "general")
    valid_types = {"issue", "feature", "general", "success_story"}
    if feedback_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid type: {feedback_type}")
    feedback_id = f"FB-{uuid.uuid4().hex[:12].upper()}"
    from gli_flow.version import VERSION
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO feedback_records
               (id, feedback_type, title, description, gli_version, os,
                tool_versions, recent_run_id, failure_fingerprint,
                telemetry_health_summary)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                feedback_id,
                feedback_type,
                payload.get("title", ""),
                payload.get("description", ""),
                VERSION,
                payload.get("os", ""),
                json.dumps(payload.get("tool_versions", {})),
                payload.get("recent_run_id", ""),
                payload.get("failure_fingerprint", ""),
                json.dumps(payload.get("telemetry_health_summary", {})),
            ),
        )
        conn.commit()
        return {"id": feedback_id, "status": "created"}
    finally:
        conn.close()


@app.patch("/feedback/{feedback_id}")
def update_feedback(feedback_id: str, payload: dict):
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM feedback_records WHERE id = ?", (feedback_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Feedback not found")
        updates = []
        params = []
        for field in ("status", "priority_level", "title", "description"):
            if field in payload:
                updates.append(f"{field} = ?")
                params.append(payload[field])
        if payload.get("priority_score") is not None:
            updates.append("priority_score = ?")
            params.append(float(payload["priority_score"]))
        if updates:
            updates.append("updated_at = datetime('now')")
            conn.execute(
                f"UPDATE feedback_records SET {', '.join(updates)} WHERE id = ?",
                params + [feedback_id],
            )
            conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()


@app.get("/feedback/stats")
def feedback_stats():
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM feedback_records").fetchone()[0]
        by_type = conn.execute(
            "SELECT feedback_type, COUNT(*) as cnt FROM feedback_records GROUP BY feedback_type"
        ).fetchall()
        by_status = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM feedback_records GROUP BY status"
        ).fetchall()
        by_priority = conn.execute(
            "SELECT priority_level, COUNT(*) as cnt FROM feedback_records GROUP BY priority_level"
        ).fetchall()
        open_count = conn.execute(
            "SELECT COUNT(*) FROM feedback_records WHERE status = 'open'"
        ).fetchone()[0]
        return {
            "total": total,
            "open": open_count,
            "by_type": dict(by_type),
            "by_status": dict(by_status),
            "by_priority": dict(by_priority),
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Support Bundle (Phase 2)
# ═══════════════════════════════════════════════════════════════


@app.post("/support-bundle/generate")
def generate_support_bundle(payload: dict = {}):
    import zipfile
    import io
    import platform
    import subprocess
    from datetime import datetime

    buf = io.BytesIO()
    bundle_data = {}

    # Version info
    from gli_flow.version import VERSION
    bundle_data["version"] = {
        "gli_flow_version": VERSION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }

    # Tool versions
    tools = {}
    for tool in ("yosys", "openroad", "magic", "netgen", "klayout", "python3"):
        try:
            r = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=5)
            tools[tool] = r.stdout.strip()[:200] if r.returncode == 0 else None
        except Exception:
            tools[tool] = None
    bundle_data["tool_versions"] = tools

    # Telemetry health
    try:
        from failure_atlas.community_intelligence.health import TelemetryHealth
        health_checker = TelemetryHealth(get_production_db_path())
        bundle_data["telemetry_health"] = health_checker.check()
    except Exception as e:
        bundle_data["telemetry_health"] = {"error": str(e)}

    # Run metadata
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT run_id, design_name, status, qor_score, created_at FROM runs ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        bundle_data["recent_runs"] = [dict(r) for r in rows]
    except Exception:
        bundle_data["recent_runs"] = []
    finally:
        conn.close()

    # Failure fingerprints
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT signature, failure_type, severity, occurrence_count, first_seen, last_seen "
            "FROM failure_atlas_entries ORDER BY occurrence_count DESC LIMIT 20"
        ).fetchall()
        bundle_data["failure_fingerprints"] = [dict(r) for r in rows]
    except Exception:
        bundle_data["failure_fingerprints"] = []
    finally:
        conn.close()

    # Audit summary
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT event_type, status, COUNT(*) as cnt FROM telemetry_audit_log "
            "GROUP BY event_type, status ORDER BY cnt DESC LIMIT 20"
        ).fetchall()
        bundle_data["audit_summary"] = [dict(r) for r in rows]
    except Exception:
        bundle_data["audit_summary"] = []
    finally:
        conn.close()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("support_bundle.json", json.dumps(bundle_data, indent=2))

    return FileResponse(
        io.BytesIO(buf.getvalue()),
        media_type="application/zip",
        filename=f"gli-flow-bundle-{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
    )


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Product Analytics (Phase 3)
# ═══════════════════════════════════════════════════════════════


@app.post("/analytics/event")
def record_analytics_event(payload: dict):
    import uuid
    event = payload.get("event", "")
    details = payload.get("details", {})
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO community_telemetry (event, failure_type, details, created_at) VALUES (?, ?, ?, datetime('now'))",
            (event, payload.get("failure_type", ""), json.dumps(details)),
        )
        conn.commit()
        return {"status": "recorded"}
    finally:
        conn.close()


@app.get("/analytics/product")
def product_analytics():
    conn = get_connection()
    try:
        # Install success rate
        install_ok = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event = 'install_success'"
        ).fetchone()[0]
        install_fail = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event = 'install_failure'"
        ).fetchone()[0]
        install_total = install_ok + install_fail
        install_rate = round(install_ok / install_total * 100, 1) if install_total > 0 else 0

        # First run success rate
        first_ok = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event = 'first_run_success'"
        ).fetchone()[0]
        first_fail = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event = 'first_run_failure'"
        ).fetchone()[0]
        first_total = first_ok + first_fail
        first_rate = round(first_ok / first_total * 100, 1) if first_total > 0 else 0

        # Most used commands
        commands = conn.execute(
            "SELECT details, COUNT(*) as cnt FROM community_telemetry "
            "WHERE event LIKE 'command_%' GROUP BY details ORDER BY cnt DESC LIMIT 10"
        ).fetchall()

        # Most common failures
        failures = conn.execute(
            "SELECT failure_type, COUNT(*) as cnt FROM failure_atlas_entries "
            "GROUP BY failure_type ORDER BY cnt DESC LIMIT 10"
        ).fetchall()

        # Most common resolutions
        resolutions = conn.execute(
            "SELECT resolution_type, COUNT(*) as cnt FROM resolution_patterns "
            "WHERE resolution_type IS NOT NULL GROUP BY resolution_type ORDER BY cnt DESC LIMIT 10"
        ).fetchall()

        # Failure Atlas views
        atlas_views = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event = 'atlas_view'"
        ).fetchone()[0]

        # AI investigation usage
        ai_usage = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE llm_investigation_status IS NOT NULL"
        ).fetchone()[0]

        # Dashboard usage
        dashboard_views = conn.execute(
            "SELECT COUNT(*) FROM community_telemetry WHERE event LIKE 'dashboard_%'"
        ).fetchone()[0]

        # User count
        session_count = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM user_journey_events"
        ).fetchone()[0]

        return {
            "install": {"success": install_ok, "failures": install_fail, "rate": install_rate},
            "first_run": {"success": first_ok, "failures": first_fail, "rate": first_rate},
            "most_used_commands": [dict(r) for r in commands],
            "most_common_failures": [dict(r) for r in failures],
            "most_common_resolutions": [dict(r) for r in resolutions],
            "atlas_views": atlas_views,
            "ai_investigation_usage": ai_usage,
            "dashboard_usage": dashboard_views,
            "unique_sessions": session_count,
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — User Journey (Phase 4)
# ═══════════════════════════════════════════════════════════════


@app.post("/journey/event")
def record_journey_event(payload: dict):
    import uuid
    event_id = f"JE-{uuid.uuid4().hex[:12].upper()}"
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO user_journey_events
               (id, session_id, stage, event_type, details, duration_sec)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                event_id,
                payload.get("session_id", ""),
                payload.get("stage", ""),
                payload.get("event_type", ""),
                json.dumps(payload.get("details", {})),
                payload.get("duration_sec", 0),
            ),
        )
        conn.commit()
        return {"id": event_id, "status": "recorded"}
    finally:
        conn.close()


@app.get("/journey")
def get_journey(
    session_id: str = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    conn = get_connection()
    try:
        if session_id:
            rows = conn.execute(
                "SELECT * FROM user_journey_events WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM user_journey_events ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return {"results": [dict(r) for r in rows]}
    finally:
        conn.close()


@app.get("/journey/report")
def journey_report():
    conn = get_connection()
    try:
        # Stage counts (funnel)
        stages = conn.execute(
            "SELECT stage, COUNT(DISTINCT session_id) as cnt FROM user_journey_events GROUP BY stage ORDER BY cnt DESC"
        ).fetchall()

        # Drop-off: sessions that started install but never reached first_run
        install_sessions = set(
            r[0] for r in conn.execute(
                "SELECT DISTINCT session_id FROM user_journey_events WHERE stage = 'install'"
            ).fetchall()
        )
        first_run_sessions = set(
            r[0] for r in conn.execute(
                "SELECT DISTINCT session_id FROM user_journey_events WHERE stage = 'first_run'"
            ).fetchall()
        )
        failure_sessions = set(
            r[0] for r in conn.execute(
                "SELECT DISTINCT session_id FROM user_journey_events WHERE stage = 'failure'"
            ).fetchall()
        )
        success_sessions = set(
            r[0] for r in conn.execute(
                "SELECT DISTINCT session_id FROM user_journey_events WHERE stage = 'success'"
            ).fetchall()
        )
        install_to_first = len(first_run_sessions) / len(install_sessions) * 100 if install_sessions else 0
        first_to_failure = len(failure_sessions) / len(first_run_sessions) * 100 if first_run_sessions else 0
        failure_to_success = len(success_sessions) / len(failure_sessions) * 100 if failure_sessions else 0

        # Average time per stage
        stage_times = conn.execute(
            "SELECT stage, AVG(duration_sec) as avg_sec FROM user_journey_events "
            "WHERE duration_sec > 0 GROUP BY stage"
        ).fetchall()

        return {
            "funnel": [dict(r) for r in stages],
            "drop_off": {
                "install_to_first_run": {"rate": round(install_to_first, 1), "total_installers": len(install_sessions), "reached_first_run": len(first_run_sessions)},
                "first_run_to_failure": {"rate": round(first_to_failure, 1), "total_first_run": len(first_run_sessions), "reached_failure": len(failure_sessions)},
                "failure_to_success": {"rate": round(failure_to_success, 1), "total_failures": len(failure_sessions), "reached_success": len(success_sessions)},
            },
            "avg_stage_duration_sec": [dict(r) for r in stage_times],
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Failure Atlas Growth Metrics (Phase 5)
# ═══════════════════════════════════════════════════════════════


@app.get("/atlas/trust-summary")
def atlas_trust_summary():
    conn = get_connection()
    try:
        verified = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification = 'VERIFIED'"
        ).fetchone()[0]
        heuristic = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification = 'HEURISTIC'"
        ).fetchone()[0]
        unverified = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE detection_classification = 'UNVERIFIED'"
        ).fetchone()[0]
        total = verified + heuristic + unverified
        trust_score = round(verified / total * 100, 1) if total > 0 else 0.0

        breakdown = conn.execute(
            "SELECT detection_classification, failure_type, COUNT(*) as cnt "
            "FROM failure_atlas_entries "
            "WHERE detection_classification IS NOT NULL AND detection_classification != '' "
            "GROUP BY detection_classification, failure_type "
            "ORDER BY detection_classification, cnt DESC"
        ).fetchall()

        return {
            "total_entries": total,
            "verified": verified,
            "heuristic": heuristic,
            "unverified": unverified,
            "atlas_trust_score": trust_score,
            "trust_level": "TRUSTED" if trust_score >= 80 else ("PARTIAL" if trust_score >= 50 else "UNTRUSTWORTHY"),
            "breakdown": [dict(r) for r in breakdown],
        }
    finally:
        conn.close()


@app.get("/atlas/metrics")
def atlas_metrics():
    conn = get_connection()
    try:
        known = conn.execute("SELECT COUNT(*) FROM failure_atlas_entries").fetchone()[0]
        unknown = conn.execute("SELECT COUNT(*) FROM community_unknown_dataset").fetchone()[0]
        total = known + unknown if known + unknown > 0 else 1
        coverage = round(known / total * 100, 1)
        miss_rate = round(unknown / total * 100, 1) if total > 0 else 0

        top_missing = conn.execute(
            "SELECT failure_type, signature, frequency FROM community_unknown_dataset ORDER BY frequency DESC LIMIT 10"
        ).fetchall()

        top_requested = conn.execute(
            "SELECT failure_type, COUNT(*) as cnt FROM community_escalations GROUP BY failure_type ORDER BY cnt DESC LIMIT 10"
        ).fetchall()

        return {
            "known_failures": known,
            "unknown_failures": unknown,
            "atlas_coverage": coverage,
            "atlas_miss_rate": miss_rate,
            "top_missing_signatures": [dict(r) for r in top_missing],
            "top_requested_entries": [dict(r) for r in top_requested],
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Resolution Intelligence Metrics (Phase 6)
# ═══════════════════════════════════════════════════════════════


@app.get("/resolutions/metrics")
def resolution_metrics():
    conn = get_connection()
    try:
        suggested = conn.execute("SELECT COUNT(*) FROM resolution_tracking").fetchone()[0]
        accepted = conn.execute(
            "SELECT COUNT(*) FROM resolution_tracking WHERE accepted_at IS NOT NULL"
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM resolution_tracking WHERE rejected_at IS NOT NULL"
        ).fetchone()[0]
        verified = conn.execute(
            "SELECT COUNT(*) FROM resolution_tracking WHERE success_verified = 1"
        ).fetchone()[0]
        success_rate = round(accepted / suggested * 100, 1) if suggested > 0 else 0

        # Trust distribution from resolution_patterns
        trust_dist = conn.execute(
            "SELECT trust_level, COUNT(*) as cnt FROM resolution_patterns GROUP BY trust_level"
        ).fetchall()

        return {
            "resolution_suggested": suggested,
            "resolution_accepted": accepted,
            "resolution_rejected": rejected,
            "resolution_success_verified": verified,
            "resolution_success_rate": success_rate,
            "trust_distribution": [dict(r) for r in trust_dist],
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Beta Dashboard (Phase 7)
# ═══════════════════════════════════════════════════════════════


@app.get("/beta/dashboard")
def beta_dashboard():
    conn = get_connection()
    try:
        # Users metrics
        total_sessions = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM user_journey_events"
        ).fetchone()[0]
        active_today = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM user_journey_events WHERE created_at >= datetime('now', '-1 day')"
        ).fetchone()[0]

        # Feedback metrics
        open_feedback = conn.execute(
            "SELECT COUNT(*) FROM feedback_records WHERE status = 'open'"
        ).fetchone()[0]
        total_feedback = conn.execute("SELECT COUNT(*) FROM feedback_records").fetchone()[0]

        # Issue metrics
        open_issues = conn.execute(
            "SELECT COUNT(*) FROM feedback_records WHERE feedback_type = 'issue' AND status = 'open'"
        ).fetchone()[0]

        # Atlas coverage
        known = conn.execute("SELECT COUNT(*) FROM failure_atlas_entries").fetchone()[0]
        unknown = conn.execute("SELECT COUNT(*) FROM community_unknown_dataset").fetchone()[0]
        atlas_total = known + unknown if known + unknown > 0 else 1
        coverage = round(known / atlas_total * 100, 1)

        # Resolution performance
        suggested = conn.execute("SELECT COUNT(*) FROM resolution_tracking").fetchone()[0]
        accepted = conn.execute(
            "SELECT COUNT(*) FROM resolution_tracking WHERE accepted_at IS NOT NULL"
        ).fetchone()[0]
        res_rate = round(accepted / suggested * 100, 1) if suggested > 0 else 0

        # Telemetry health
        tel_healthy = conn.execute(
            "SELECT COUNT(*) FROM telemetry_audit_log WHERE status = 'healthy'"
        ).fetchone()[0]
        tel_critical = conn.execute(
            "SELECT COUNT(*) FROM telemetry_audit_log WHERE status = 'critical'"
        ).fetchone()[0]

        # System health
        total_runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        failed_runs = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE status = 'FAILED'"
        ).fetchone()[0]
        success_rate = round((total_runs - failed_runs) / total_runs * 100, 1) if total_runs > 0 else 0

        return {
            "users": {"total_sessions": total_sessions, "active_today": active_today},
            "feedback": {"open": open_feedback, "total": total_feedback},
            "issues": {"open": open_issues},
            "atlas": {"known": known, "unknown": unknown, "coverage": coverage},
            "resolutions": {"suggested": suggested, "accepted": accepted, "success_rate": res_rate},
            "telemetry": {"healthy": tel_healthy, "critical": tel_critical},
            "system": {"total_runs": total_runs, "failed_runs": failed_runs, "success_rate": success_rate},
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Prioritization Engine (Phase 8)
# ═══════════════════════════════════════════════════════════════


@app.post("/feedback/{feedback_id}/prioritize")
def prioritize_feedback(feedback_id: str):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, feedback_type, status, priority_score FROM feedback_records WHERE id = ?",
            (feedback_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Feedback not found")

        # Compute priority based on:
        # - Frequency: how often similar issues appear (0-25)
        # - Severity: based on type (0-25)
        # - Affected users: how many distinct sessions reported (0-25)
        # - Trust impact: based on feedback type (0-25)

        frequency_score = 0
        row2 = conn.execute(
            "SELECT COUNT(*) as cnt FROM feedback_records WHERE feedback_type = ? AND status != 'closed'",
            (row["feedback_type"],),
        ).fetchone()
        if row2:
            cnt = row2[0]
            frequency_score = min(25, cnt * 5)

        severity_map = {"issue": 25, "feature": 15, "general": 10, "success_story": 5}
        severity_score = severity_map.get(row["feedback_type"], 10)

        affected_users = 0
        row3 = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM user_journey_events"
        ).fetchone()
        if row3:
            affected_users = min(25, row3[0] * 2)

        trust_map = {"issue": 25, "feature": 10, "general": 15, "success_story": 20}
        trust_score = trust_map.get(row["feedback_type"], 10)

        total_score = frequency_score + severity_score + affected_users + trust_score

        if total_score >= 70:
            level = "HIGH"
        elif total_score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"

        conn.execute(
            "UPDATE feedback_records SET priority_score = ?, priority_level = ?, updated_at = datetime('now') WHERE id = ?",
            (total_score, level, feedback_id),
        )
        conn.commit()

        return {
            "feedback_id": feedback_id,
            "priority_score": total_score,
            "priority_level": level,
            "factors": {
                "frequency": frequency_score,
                "severity": severity_score,
                "affected_users": affected_users,
                "trust_impact": trust_score,
            },
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Weekly Product Report (Phase 9)
# ═══════════════════════════════════════════════════════════════


@app.get("/beta/report")
def weekly_beta_report():
    conn = get_connection()
    try:
        # New sessions this week
        new_users = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM user_journey_events WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]

        # New failures this week
        new_failures = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE status = 'FAILED' AND created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]

        # Atlas growth
        atlas_growth = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]

        # Resolution growth
        res_growth = conn.execute(
            "SELECT COUNT(*) FROM resolution_patterns WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]

        # Top pain points (most frequent failures)
        pain_points = conn.execute(
            "SELECT failure_type, COUNT(*) as cnt FROM failure_atlas_entries "
            "WHERE created_at >= datetime('now', '-7 days') GROUP BY failure_type ORDER BY cnt DESC LIMIT 5"
        ).fetchall()

        # Most requested features
        features = conn.execute(
            "SELECT title, COUNT(*) as cnt FROM feedback_records "
            "WHERE feedback_type = 'feature' AND created_at >= datetime('now', '-7 days') "
            "GROUP BY title ORDER BY cnt DESC LIMIT 5"
        ).fetchall()

        # Feedback this week
        feedback_week = conn.execute(
            "SELECT COUNT(*) FROM feedback_records WHERE created_at >= datetime('now', '-7 days')"
        ).fetchone()[0]

        # Open issues
        open_issues = conn.execute(
            "SELECT COUNT(*) FROM feedback_records WHERE status = 'open'"
        ).fetchone()[0]

        return {
            "report_period": "last_7_days",
            "new_users": new_users,
            "new_failures": new_failures,
            "atlas_growth": atlas_growth,
            "resolution_growth": res_growth,
            "feedback_submitted": feedback_week,
            "open_issues": open_issues,
            "top_pain_points": [dict(r) for r in pain_points],
            "most_requested_features": [dict(r) for r in features],
            "generated_at": datetime.now().isoformat(),
        }
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════
# BETA OPERATIONS — Record analytics events from dashboard
# ═══════════════════════════════════════════════════════════════


@app.post("/record-event")
def record_event(payload: dict):
    event = payload.get("event", "")
    details = payload.get("details", {})
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO community_telemetry (event, details, created_at) VALUES (?, ?, datetime('now'))",
            (event, json.dumps(details)),
        )
        conn.commit()
        return {"status": "recorded"}
    finally:
        conn.close()


_dashboard_dist = str(Path(__file__).resolve().parent.parent / "dashboard" / "dist")
if os.path.isdir(_dashboard_dist):
    app.mount("/", StaticFiles(directory=_dashboard_dist, html=True), name="dashboard")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("backend.server:app", host="127.0.0.1", port=port, reload=True)

