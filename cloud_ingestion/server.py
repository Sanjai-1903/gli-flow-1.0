"""FastAPI ingest server.

Authentication:
    Every request to /api/v1/telemetry (and /api/v1/stats) must present a
    valid Bearer token in the Authorization header. The token is issued by
    the web app and validated against public.user_cli_tokens. The user_id
    associated with the token is attached to every row written on behalf
    of that request.

    In dev mode (config.auth.enabled=False) validation is skipped and
    every request is treated as the legacy/dev user.
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from cloud_ingestion.config import CloudIngestionConfig
from cloud_ingestion.database import IngestionDatabase
from cloud_ingestion.auth import make_auth_dependency
from cloud_ingestion.routes_cli import build_router as build_cli_router
from cloud_ingestion.routes_legacy import build_router as build_legacy_router
from cloud_ingestion.models import (
    UploadPayload,
    UploadResponse,
    HealthResponse,
    StatsResponse,
)

logger = logging.getLogger(__name__)

_start_time = time.time()


class CloudIngestionServer:
    def __init__(self, config: Optional[CloudIngestionConfig] = None):
        self.config = config or CloudIngestionConfig.load()
        self.db = IngestionDatabase(self.config)
        self.db.initialize()
        self._auth_dep = make_auth_dependency(self.config)

    def create_app(self) -> FastAPI:
        app = FastAPI(
            title="GLI Flow Cloud Ingestion",
            version="2.0.0",
            description="Per-user telemetry ingestion with Bearer-token auth",
        )

        # CORS: we authenticate via Authorization headers, not cookies, so
        # credentials stay off — that lets us use the wildcard origin from
        # config (which the browser rejects when credentials=True).
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors.allowed_origins,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

        auth_dep = self._auth_dep

        @app.post("/api/v1/telemetry", response_model=UploadResponse)
        async def ingest_telemetry(
            payload: UploadPayload,
            request: Request,
            user_id: str = Depends(auth_dep),
        ):
            batch_id = str(uuid.uuid4())
            source_ip = request.client.host if request.client else ""

            telemetry_count = 0
            failures_count = 0
            escalations_count = 0

            try:
                if payload.telemetry_events:
                    events_dict = [e.model_dump() for e in payload.telemetry_events]
                    telemetry_count = self.db.insert_telemetry_events(
                        events_dict, batch_id, source_ip, user_id=user_id
                    )

                if payload.failure_atlas_entries:
                    entries_dict = [e.model_dump() for e in payload.failure_atlas_entries]
                    failures_count = self.db.insert_failure_entries(
                        entries_dict, batch_id, user_id=user_id
                    )

                escalations_count = len(payload.escalations)
                for esc in payload.escalations:
                    self.db.record_consent(
                        esc.run_id,
                        esc.consent_record.get("consent_given", False),
                        esc.consent_record.get("consent_timestamp", ""),
                        user_id=user_id,
                    )

                self.db.record_upload_audit(
                    run_id=payload.run_id,
                    batch_id=batch_id,
                    telemetry_count=telemetry_count,
                    failures_count=failures_count,
                    escalations_count=escalations_count,
                    source_version=payload.source_version,
                    client_ip=source_ip,
                    status="accepted",
                    user_id=user_id,
                )

                logger.info(
                    "Ingested user=%s run=%s batch=%s telemetry=%d failures=%d escalations=%d",
                    user_id, payload.run_id, batch_id, telemetry_count, failures_count, escalations_count,
                )

                return UploadResponse(
                    status="accepted",
                    run_id=payload.run_id,
                    telemetry_accepted=telemetry_count,
                    failures_accepted=failures_count,
                    escalations_accepted=escalations_count,
                    upload_id=batch_id,
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error("Ingestion failed for user=%s run=%s: %s", user_id, payload.run_id, e)
                self.db.record_upload_audit(
                    run_id=payload.run_id,
                    batch_id=batch_id,
                    telemetry_count=telemetry_count,
                    failures_count=failures_count,
                    escalations_count=escalations_count,
                    source_version=payload.source_version,
                    client_ip=source_ip,
                    status="failed",
                    error_message=str(e),
                    user_id=user_id,
                )
                raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

        @app.get("/api/v1/health", response_model=HealthResponse)
        async def health():
            # Unauthenticated on purpose — used by Render/uptime checks.
            return HealthResponse(
                status="ok",
                database="connected",
                uptime_sec=time.time() - _start_time,
            )

        @app.get("/api/v1/stats", response_model=StatsResponse)
        async def stats(user_id: str = Depends(auth_dep)):
            # Scoped to the caller's own data.
            db_stats = self.db.get_stats(user_id=user_id)
            return StatsResponse(**db_stats)

        @app.get("/api/v1/whoami")
        async def whoami(user_id: str = Depends(auth_dep)):
            # Handy for the CLI to verify its token works.
            return {"user_id": user_id, "authenticated": True}

        # Device-flow login + CLI token management (Supabase-JWT authed)
        app.include_router(build_cli_router(self.config))

        # Legacy dashboard endpoints (Supabase-JWT authed, per-user).
        # Mounted under /api/v1/legacy/*, called from the dashboard via
        # a global fetch wrapper that rewrites bare paths (`/runs`, etc.).
        app.include_router(build_legacy_router(self.config))

        # Catch-all so unhandled exceptions still pass through CORS. Without
        # this, browsers see an "access-control-allow-origin missing" error
        # instead of the actual 500 detail.
        @app.exception_handler(Exception)
        async def _catch_all(request: Request, exc: Exception):
            logger.exception("Unhandled server error on %s: %s", request.url.path, exc)
            return JSONResponse(
                status_code=500,
                content={"detail": f"{type(exc).__name__}: {exc}"[:500]},
            )

        return app


def create_app(config: Optional[CloudIngestionConfig] = None) -> FastAPI:
    server = CloudIngestionServer(config)
    return server.create_app()


if __name__ == "__main__":
    import uvicorn
    cfg = CloudIngestionConfig.load()
    uvicorn.run(
        "cloud_ingestion.server:create_app",
        host=cfg.server.host,
        port=cfg.server.port,
        log_level=cfg.server.log_level.lower(),
        workers=cfg.server.workers,
    )
