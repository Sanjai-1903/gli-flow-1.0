"""
Mandatory Failure Corpus Entries.

Each entry documents a historical bug with reproduce/verify/prevent.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class CorpusEntry:
    entry_id: str
    title: str
    description: str
    reproduce_fn: Optional[Callable[[], None]] = None
    verify_fn: Optional[Callable[[], bool]] = None
    prevent_fn: Optional[Callable[[], None]] = None
    affected_files: list[str] = field(default_factory=list)
    fix_commit: str = ""
    fixed_in_version: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "description": self.description,
            "affected_files": self.affected_files,
            "fix_commit": self.fix_commit,
            "fixed_in_version": self.fixed_in_version,
        }


FAILURE_CORPUS: dict[str, CorpusEntry] = {}


def _register(entry: CorpusEntry) -> CorpusEntry:
    FAILURE_CORPUS[entry.entry_id] = entry
    return entry


CORPUS_ENTRY_1_MAGIC_OLD_VERSION = _register(CorpusEntry(
    entry_id="magic_old_version_selected",
    title="Magic old/broken version selected over user-installed newer version",
    description=(
        "When both a system-installed Magic (8.3.105, known broken) "
        "and a user-installed Magic (8.3.659) exist, the discovery logic "
        "must select the user-installed version. The broken version causes "
        "DRC false positives and missing violation reports."
    ),
    affected_files=["gli_flow/core/tool_discovery.py"],
    fix_commit="tool_discovery: implement deterministic precedence",
))

CORPUS_ENTRY_2_MISSING_DRC_REPORT = _register(CorpusEntry(
    entry_id="missing_drc_report",
    title="Missing DRC report silently treated as zero violations",
    description=(
        "When Magic or KLayout DRC does not produce a report file, "
        "the pipeline must report ERROR, not PASS. Previously, a missing "
        "report was treated as zero violations, masking tool failures."
    ),
    affected_files=["gli_flow/core/drc_runner.py"],
    fix_commit="drc_runner: return ERROR for missing reports",
))

CORPUS_ENTRY_3_EMPTY_DRC_REPORT = _register(CorpusEntry(
    entry_id="empty_drc_report",
    title="Empty DRC report parsed as zero violations",
    description=(
        "An empty DRC report file (0 bytes) must be treated as ERROR, "
        "not as PASS with zero violations. Empty reports indicate a tool "
        "failure during DRC execution."
    ),
    affected_files=["gli_flow/core/drc_runner.py"],
    fix_commit="drc_runner: validate non-zero report size",
))

CORPUS_ENTRY_4_MISSING_SPICE_INCLUDE = _register(CorpusEntry(
    entry_id="missing_spice_include",
    title="Missing SPICE include in LVS causes silent failure",
    description=(
        "When the SPICE netlist references an include file that does not exist, "
        "Netgen LVS may report PASS with zero comparisons. Flow must detect "
        "missing include files and report ERROR."
    ),
    affected_files=["gli_flow/backends/openroad_adapter.py"],
))

CORPUS_ENTRY_5_POWER_NET_MISMATCH = _register(CorpusEntry(
    entry_id="power_net_mismatch",
    title="Power net name mismatch between synthesis and P&R",
    description=(
        "When the power net name in the synthesized netlist does not match "
        "the PDK power grid definition, the flow produces unconnected power "
        "nets. The signoff gate must detect this mismatch."
    ),
    affected_files=["gli_flow/backends/openroad_adapter.py"],
))

CORPUS_ENTRY_6_MANIFEST_TOP_MODULE_MISMATCH = _register(CorpusEntry(
    entry_id="manifest_top_module_mismatch",
    title="Manifest top_module does not match RTL hierarchy",
    description=(
        "When gli_manifest.yaml specifies a top_module that does not exist "
        "in the RTL sources, synthesis blackboxes the entire design. "
        "The pre-synthesis hierarchy check must detect this."
    ),
    affected_files=["gli_flow/core/synthesis_safety.py"],
))

CORPUS_ENTRY_7_SYNTHETIC_CLEAN_BUG = _register(CorpusEntry(
    entry_id="synthetic_clean_bug",
    title="Tool reports PASS with zero actual comparisons",
    description=(
        "A synthetic bug where an EDA tool exits with code 0 and produces "
        "a PASS report but performed zero actual comparisons (e.g., empty "
        "LVS comparison). The flow must detect zero-comparison PASS results."
    ),
    affected_files=["gli_flow/core/contracts/tool_result.py"],
))

CORPUS_ENTRY_8_TOOL_FAILURE_MARKED_CLEAN = _register(CorpusEntry(
    entry_id="tool_failure_marked_clean",
    title="Tool execution failure reported as PASS/clean",
    description=(
        "When an EDA tool fails to execute (non-zero exit code, crash, OOM), "
        "the flow must report FAIL or ERROR. Previously, some tool failures "
        "were caught by broad except handlers that returned PASS."
    ),
    affected_files=["gli_flow/core/orchestrator.py"],
    fix_commit="exception_audit: replace SILENT_SUCCESS patterns",
))

CORPUS_ENTRY_9_CORRUPT_ARTIFACT = _register(CorpusEntry(
    entry_id="corrupt_artifact",
    title="Corrupt artifact treated as valid",
    description=(
        "A corrupt GDS file (invalid header, truncated) must be detected "
        "by the artifact validator. Previously, any existing file passed signoff."
    ),
    affected_files=["gli_flow/core/validation/artifact_validator.py"],
))

CORPUS_ENTRY_10_MISSING_ARTIFACT = _register(CorpusEntry(
    entry_id="missing_artifact",
    title="Missing artifact treated as PASS",
    description=(
        "When a required artifact (GDS, DEF, netlist) is missing, the signoff "
        "gate must report ERROR. Previously, missing artifacts were handled "
        "inconsistently across stages."
    ),
    affected_files=["gli_flow/core/orchestrator.py"],
    fix_commit="signoff: mandatory artifact validation",
))


def list_corpus() -> list[CorpusEntry]:
    return list(FAILURE_CORPUS.values())


def get_entry(entry_id: str) -> Optional[CorpusEntry]:
    return FAILURE_CORPUS.get(entry_id)


def corpus_report() -> str:
    lines = ["# Failure Corpus Report", ""]
    for eid, entry in sorted(FAILURE_CORPUS.items()):
        lines.append(f"## {eid}")
        lines.append(f"- **Title**: {entry.title}")
        lines.append(f"- **Description**: {entry.description}")
        lines.append(f"- **Affected files**: {', '.join(entry.affected_files)}")
        lines.append("")
    return "\n".join(lines)
