"""
Artifact Validation Framework.

Every report must pass:
  - Exists
  - Non-zero size
  - Parseable
  - Required structure present
  - Generated during current run

Empty report = ERROR
Corrupt report = ERROR
Missing report = ERROR
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)


class ValidationLevel(Enum):
    EXISTS = "exists"
    NONZERO = "nonzero"
    PARSEABLE = "parseable"
    STRUCTURE = "structure"
    FRESHNESS = "freshness"


class ArtifactType(Enum):
    DRC_REPORT = "drc_report"
    LVS_REPORT = "lvs_report"
    STA_REPORT = "sta_report"
    POWER_REPORT = "power_report"
    TIMING_REPORT = "timing_report"
    GDS = "gds"
    DEF = "def"
    NETLIST = "netlist"
    METRICS = "metrics"
    LOG = "log"
    JSON = "json"
    CONFIG = "config"
    MANIFEST = "manifest"
    CUSTOM = "custom"


@dataclass
class StructureCheck:
    name: str
    validator: Callable[[str], bool]

    def __call__(self, content: str) -> bool:
        try:
            return self.validator(content)
        except Exception:
            return False


@dataclass
class ArtifactValidationResult:
    artifact_path: str
    artifact_type: ArtifactType
    levels_passed: list[ValidationLevel] = field(default_factory=list)
    levels_failed: list[ValidationLevel] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    detail: str = ""

    @property
    def passed(self) -> bool:
        return len(self.levels_failed) == 0

    @property
    def status(self) -> str:
        if self.passed:
            return "PASS"
        if ValidationLevel.EXISTS in self.levels_failed:
            return "ERROR"
        if ValidationLevel.PARSEABLE in self.levels_failed:
            return "ERROR"
        return "FAIL"


DEFAULT_STRUCTURE_CHECKS: dict[ArtifactType, list[StructureCheck]] = {
    ArtifactType.DRC_REPORT: [
        StructureCheck("has_violations", lambda c: "violation" in c.lower()),
        StructureCheck("has_total_count", lambda c: bool(re.search(r"total.*violation", c, re.IGNORECASE))),
    ],
    ArtifactType.LVS_REPORT: [
        StructureCheck("has_device_count", lambda c: bool(re.search(r"device", c, re.IGNORECASE))),
        StructureCheck("has_net_count", lambda c: bool(re.search(r"net", c, re.IGNORECASE))),
    ],
    ArtifactType.STA_REPORT: [
        StructureCheck("has_timing", lambda c: bool(re.search(r"(wns|tns|slack|setup|hold)", c, re.IGNORECASE))),
    ],
    ArtifactType.POWER_REPORT: [
        StructureCheck("has_power", lambda c: bool(re.search(r"(power|mw|current|voltage)", c, re.IGNORECASE))),
    ],
    ArtifactType.TIMING_REPORT: [
        StructureCheck("has_timing_data", lambda c: bool(re.search(r"(wns|tns|slack|delay|path)", c, re.IGNORECASE))),
    ],
    ArtifactType.JSON: [
        StructureCheck("is_valid_json", lambda c: bool(json.loads(c))),
    ],
}


class ArtifactValidator:
    def __init__(self, run_dir: str):
        self.run_dir = Path(run_dir)
        self.results: list[ArtifactValidationResult] = []
        self.run_start_time: Optional[datetime] = None

    def set_run_start_time(self, dt: datetime) -> None:
        self.run_start_time = dt

    def validate(
        self,
        rel_path: str,
        artifact_type: ArtifactType = ArtifactType.CUSTOM,
        required_structure: str = None,
        structure_checks: list[StructureCheck] = None,
        max_age_seconds: float = None,
    ) -> ArtifactValidationResult:
        full_path = self.run_dir / rel_path
        result = ArtifactValidationResult(
            artifact_path=rel_path,
            artifact_type=artifact_type,
        )

        if not full_path.exists():
            result.levels_failed.append(ValidationLevel.EXISTS)
            result.errors.append(f"Artifact not found: {full_path}")
            self.results.append(result)
            return result
        result.levels_passed.append(ValidationLevel.EXISTS)

        if full_path.stat().st_size == 0:
            result.levels_failed.append(ValidationLevel.NONZERO)
            result.errors.append(f"Artifact is empty (zero size): {full_path}")
            self.results.append(result)
            return result
        result.levels_passed.append(ValidationLevel.NONZERO)

        try:
            if artifact_type == ArtifactType.JSON:
                content = full_path.read_text()
                json.loads(content)
            else:
                content = full_path.read_text(errors="replace")
            result.levels_passed.append(ValidationLevel.PARSEABLE)
        except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
            result.levels_failed.append(ValidationLevel.PARSEABLE)
            result.errors.append(f"Cannot parse {full_path}: {e}")
            self.results.append(result)
            return result

        checks = structure_checks or DEFAULT_STRUCTURE_CHECKS.get(artifact_type, [])
        if required_structure:
            checks.append(StructureCheck("required_structure", lambda c: required_structure in c))

        if checks:
            all_structure_ok = True
            for check in checks:
                if not check(content):
                    all_structure_ok = False
                    result.errors.append(f"Structure check '{check.name}' failed for {full_path}")
            if all_structure_ok:
                result.levels_passed.append(ValidationLevel.STRUCTURE)
            else:
                result.levels_failed.append(ValidationLevel.STRUCTURE)

        if max_age_seconds is not None and self.run_start_time:
            mtime = datetime.fromtimestamp(full_path.stat().st_mtime, tz=timezone.utc)
            age = (mtime - self.run_start_time).total_seconds()
            if age > max_age_seconds or age < 0:
                result.levels_failed.append(ValidationLevel.FRESHNESS)
                result.errors.append(f"Artifact {full_path} has invalid age: {age}s")
            else:
                result.levels_passed.append(ValidationLevel.FRESHNESS)

        self.results.append(result)
        return result

    def validate_report(
        self,
        rel_path: str,
        required_content: str = None,
        max_age_seconds: float = 86400,
    ) -> ArtifactValidationResult:
        return self.validate(
            rel_path=rel_path,
            artifact_type=ArtifactType.DRC_REPORT,
            required_structure=required_content,
            max_age_seconds=max_age_seconds,
        )

    def validate_gds(self, rel_path: str = "artifacts/6_final.gds") -> ArtifactValidationResult:
        full_path = self.run_dir / rel_path
        result = ArtifactValidationResult(
            artifact_path=rel_path,
            artifact_type=ArtifactType.GDS,
        )
        if not full_path.exists():
            result.levels_failed.append(ValidationLevel.EXISTS)
            result.errors.append(f"GDS not found: {full_path}")
        elif full_path.stat().st_size == 0:
            result.levels_failed.append(ValidationLevel.NONZERO)
            result.errors.append(f"GDS is empty: {full_path}")
        else:
            result.levels_passed.extend([ValidationLevel.EXISTS, ValidationLevel.NONZERO])
            with open(full_path, "rb") as f:
                header = f.read(4)
            if header == b"\x00\x00\x00\x00":
                result.detail = "GDS binary header detected"
                result.levels_passed.append(ValidationLevel.PARSEABLE)
            else:
                result.levels_failed.append(ValidationLevel.PARSEABLE)
                result.errors.append("Invalid GDS header")

        self.results.append(result)
        return result

    def summary(self) -> dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "status": "PASS" if failed == 0 else "ERROR",
            "results": [r for r in self.results if not r.passed],
        }
