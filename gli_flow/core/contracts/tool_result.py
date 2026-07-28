"""
Standard ToolResult contract for all EDA tool adapters.

Every adapter method must return a ToolResult.
No custom status formats are allowed outside this module.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    NOT_RUN = "NOT_RUN"


@dataclass
class ToolResult:
    tool_name: str
    tool_version: str
    status: Status
    execution_success: bool
    artifact_present: bool
    validation_success: bool
    runtime_seconds: float
    return_code: int
    evidence: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def pass_result(
        cls,
        tool_name: str,
        tool_version: str = "",
        runtime_seconds: float = 0.0,
        return_code: int = 0,
        evidence: dict[str, Any] = None,
        metrics: dict[str, Any] = None,
        warnings: list[str] = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            tool_version=tool_version,
            status=Status.PASS,
            execution_success=True,
            artifact_present=True,
            validation_success=True,
            runtime_seconds=runtime_seconds,
            return_code=return_code,
            evidence=evidence or {},
            warnings=warnings or [],
            errors=[],
            metrics=metrics or {},
        )

    @classmethod
    def fail_result(
        cls,
        tool_name: str,
        tool_version: str = "",
        runtime_seconds: float = 0.0,
        return_code: int = -1,
        evidence: dict[str, Any] = None,
        metrics: dict[str, Any] = None,
        warnings: list[str] = None,
        errors: list[str] = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            tool_version=tool_version,
            status=Status.FAIL,
            execution_success=False,
            artifact_present=False,
            validation_success=False,
            runtime_seconds=runtime_seconds,
            return_code=return_code,
            evidence=evidence or {},
            warnings=warnings or [],
            errors=errors or [],
            metrics=metrics or {},
        )

    @classmethod
    def error_result(
        cls,
        tool_name: str,
        error: str,
        tool_version: str = "",
        errors: list[str] = None,
        evidence: dict[str, Any] = None,
    ) -> "ToolResult":
        return cls(
            tool_name=tool_name,
            tool_version=tool_version,
            status=Status.ERROR,
            execution_success=False,
            artifact_present=False,
            validation_success=False,
            runtime_seconds=0.0,
            return_code=-1,
            evidence=evidence or {},
            warnings=[],
            errors=errors or [error],
            metrics={},
        )

    @classmethod
    def not_run(cls, tool_name: str, reason: str = "") -> "ToolResult":
        return cls(
            tool_name=tool_name,
            tool_version="",
            status=Status.NOT_RUN,
            execution_success=False,
            artifact_present=False,
            validation_success=False,
            runtime_seconds=0.0,
            return_code=-1,
            evidence={},
            warnings=[],
            errors=[reason] if reason else [],
            metrics={},
        )

    @classmethod
    def from_legacy(
        cls,
        tool_name: str,
        tool_version: str,
        status_str: str,
        runtime_seconds: float,
        return_code: int,
        **kwargs,
    ) -> "ToolResult":
        status_map = {
            "PASS": Status.PASS,
            "FAIL": Status.FAIL,
            "ERROR": Status.ERROR,
            "NOT_RUN": Status.NOT_RUN,
        }
        status = status_map.get(status_str.upper(), Status.ERROR)
        execution_success = kwargs.pop("execution_success", status == Status.PASS)
        artifact_present = kwargs.pop("artifact_present", status == Status.PASS)
        validation_success = kwargs.pop("validation_success", status == Status.PASS)
        evidence = kwargs.pop("evidence", {})
        warnings = kwargs.pop("warnings", [])
        errors = kwargs.pop("errors", [])
        metrics = kwargs
        return cls(
            tool_name=tool_name,
            tool_version=tool_version,
            status=status,
            execution_success=execution_success,
            artifact_present=artifact_present,
            validation_success=validation_success,
            runtime_seconds=runtime_seconds,
            return_code=return_code,
            evidence=evidence,
            warnings=warnings,
            errors=errors,
            metrics=metrics,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ToolResult":
        d = dict(d)
        d["status"] = Status(d["status"]) if isinstance(d.get("status"), str) else d.get("status", Status.ERROR)
        return cls(**d)

    @property
    def passed(self) -> bool:
        return self.status == Status.PASS

    @property
    def failed(self) -> bool:
        return self.status in (Status.FAIL, Status.ERROR)

    @property
    def is_clean(self) -> bool:
        return self.status == Status.PASS and self.validation_success

    def __bool__(self) -> bool:
        return self.status == Status.PASS
