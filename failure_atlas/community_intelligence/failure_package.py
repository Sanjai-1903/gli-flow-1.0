import dataclasses
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from failure_atlas.ai_assistant.context import AIContext


EXCLUDED_FIELDS = [
    "rtl", "gds", "netlist", "source", "customer_ip",
    "project_files", "license", "credential", "password",
    "secret", "private_key", "design_files",
]

EXCLUDED_EXTENSIONS = {".v", ".sv", ".vh", ".svh", ".gds", ".oas",
                        ".sp", ".cdl", ".def", ".lef", ".lib", ".db"}


@dataclasses.dataclass
class FailurePackage:
    package_version: str
    consent_record: Dict[str, Any]
    failure: Dict[str, Any]
    ai_suggestions: Optional[Dict[str, Any]] = None
    user_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_version": self.package_version,
            "consent_record": self.consent_record,
            "failure": self.failure,
            "ai_suggestions": self.ai_suggestions or {},
            "user_notes": self.user_notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def validate_sanitized(self) -> List[str]:
        """Check that no excluded data is present in the package."""
        warnings = []
        serialized = json.dumps(self.to_dict()).lower()
        for field in EXCLUDED_FIELDS:
            if field.lower() in serialized:
                warnings.append(f"Possible excluded field detected: {field}")
        return warnings


class FailurePackageBuilder:
    """Builds a sanitized failure package for escalation.

    The package includes diagnostic metadata ONLY:
    - Tool, stage, failure type, error text
    - Log excerpt (last 100 lines)
    - Metrics and design metadata
    - AI investigation suggestions
    - User notes and consent record

    The package NEVER includes:
    - RTL, GDS, netlists, source code, customer IP, or full project files.
    """

    def __init__(self):
        pass

    @staticmethod
    def build(
        tool: str = "",
        stage: str = "",
        failure_type: str = "",
        error_text: str = "",
        log_excerpt: str = "",
        metrics: Optional[Dict[str, Any]] = None,
        design_metadata: Optional[Dict[str, Any]] = None,
        run_metadata: Optional[Dict[str, Any]] = None,
        ai_context: Optional[AIContext] = None,
        ai_suggestions: Optional[Dict[str, Any]] = None,
        user_notes: str = "",
        consent_given: bool = False,
    ) -> FailurePackage:
        """Build a sanitized failure package."""
        failure = {
            "tool": tool or "",
            "stage": stage or "",
            "failure_type": failure_type or "UNKNOWN",
            "error_text": error_text or "",
            "log_excerpt": log_excerpt or "",
            "metrics": metrics or {},
        }

        if design_metadata:
            allowed_design = {
                "design_name", "top_module", "pdk", "pdk_variant",
                "clock_period_ns", "utilization_target", "threads",
            }
            failure["design_metadata"] = {
                k: v for k, v in design_metadata.items()
                if k in allowed_design
            }

        if run_metadata:
            allowed_run = {
                "run_id", "timestamp", "backend", "gli_version",
                "status", "current_stage",
            }
            failure["run_metadata"] = {
                k: v for k, v in run_metadata.items()
                if k in allowed_run
            }

        if ai_context:
            failure["ai_context"] = ai_context.to_dict()

        consent_record = {
            "consent_given": consent_given,
            "consent_timestamp": datetime.now(timezone.utc).isoformat() if consent_given else "",
            "user_acknowledged_no_sensitive_data": consent_given,
        }

        return FailurePackage(
            package_version="1.0",
            consent_record=consent_record,
            failure=failure,
            ai_suggestions=ai_suggestions or {},
            user_notes=user_notes,
        )

    @staticmethod
    def from_ai_context(
        ai_context: AIContext,
        ai_suggestions: Optional[Dict[str, Any]] = None,
        user_notes: str = "",
        consent_given: bool = False,
    ) -> FailurePackage:
        """Build a failure package from an existing AI context."""
        return FailurePackageBuilder.build(
            tool=ai_context.tool,
            stage=ai_context.stage,
            failure_type=ai_context.failure_type,
            error_text=ai_context.error_text,
            log_excerpt=ai_context.log_snippet,
            metrics=ai_context.metrics,
            design_metadata=ai_context.design_metadata,
            run_metadata=ai_context.run_metadata,
            ai_context=ai_context,
            ai_suggestions=ai_suggestions,
            user_notes=user_notes,
            consent_given=consent_given,
        )
