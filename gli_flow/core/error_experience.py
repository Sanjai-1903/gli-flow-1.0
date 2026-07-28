"""Structured error experience system for GLI-FLOW."""

import traceback
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GliFlowError:
    """Structured error with user-facing and debug information."""

    error_code: str
    message: str
    cause: str = ""
    evidence: str = ""
    resolution_steps: list[str] = field(default_factory=list)
    doc_link: str = ""
    debug_traceback: str = ""


_RESOLUTION_TABLE: dict[str, str] = {
    "E1001": (
        "1. Verify the tool is installed: which <tool-name>\n"
        "2. Install the missing tool: gli-flow install --tool <tool-name>\n"
        "3. Ensure the tool directory is in your PATH"
    ),
    "E1002": (
        "1. Install the PDK: gli-flow install --pdk <pdk-name>\n"
        "2. Set the PDK_ROOT environment variable\n"
        "3. Verify PDK version compatibility with your technology"
    ),
    "E1003": (
        "1. Inspect the stage logs for failure details\n"
        "2. Re-run the stage: gli-flow run --stage <stage>\n"
        "3. Check the DRC deck for errors"
    ),
    "E1004": (
        "1. Trace connectivity differences between layout and schematic\n"
        "2. Verify extracted netlist against schematic netlist\n"
        "3. Check power/ground connections and floating nodes\n"
        "4. Run: gli-flow lvs --debug for detailed output"
    ),
    "E1005": (
        "1. Increase available memory: gli-flow run --memory 32000\n"
        "2. Reduce design size or core utilization\n"
        "3. Reduce --threads to lower peak memory usage\n"
        "4. Close other memory-intensive processes"
    ),
    "E1006": (
        "1. Increase timeout: gli-flow run --timeout 14400\n"
        "2. Reduce design complexity\n"
        "3. Optimize the design for faster processing\n"
        "4. Split the design into smaller blocks"
    ),
    "E1007": (
        "1. Validate config file syntax: gli-flow validate --config\n"
        "2. Check for missing required fields\n"
        "3. Ensure all paths in config are absolute or relative to project root\n"
        "4. Refer to the configuration documentation for required schema"
    ),
    "E1008": (
        "1. Run database repair: gli-flow db repair\n"
        "2. Restore from backup: gli-flow db restore --backup <path>\n"
        "3. Check disk space and filesystem integrity"
    ),
    "E1009": (
        "1. Check YAML syntax: python -c \"import yaml; yaml.safe_load(open('gli_manifest.yaml'))\"\n"
        "2. Verify required keys: version, design, stages\n"
        "3. Ensure all stage references are valid\n"
        "4. Run: gli-flow validate --manifest"
    ),
    "E1010": (
        "1. Check the full error output above for details\n"
        "2. Verify your environment and dependencies\n"
        "3. Run: gli-flow doctor to diagnose common issues\n"
        "4. Report the issue with gli-flow --debug output"
    ),
}


def resolve_error(error_code: str) -> str:
    """Return resolution steps for a given error code."""
    return _RESOLUTION_TABLE.get(
        error_code,
        _RESOLUTION_TABLE["E1010"],
    )


_BUILDERS: dict[str, dict] = {}


def _register_error(key: str, error_code: str, message: str, cause: str,
                    resolution_steps: list[str]) -> None:
    _BUILDERS[key] = dict(
        error_code=error_code,
        message=message,
        cause=cause,
        resolution_steps=resolution_steps,
    )


_register_error(
    "MAGIC_DRC_MISSING", "E1003",
    "Magic DRC report is missing.",
    "The DRC stage completed but no report file was generated.",
    ["1. Check Magic's DRC output in the logs",
     "2. Verify the DRC deck has no syntax errors",
     "3. Re-run with: gli-flow run --stage drc"],
)
_register_error(
    "LVS_FAILURE", "E1004",
    "Layout versus schematic (LVS) mismatch detected.",
    "The netlist extracted from the layout does not match the schematic.",
    ["1. Trace differences with: gli-flow lvs --debug",
     "2. Check for missing or extra devices",
     "3. Verify connectivity of power and ground nets",
     "4. Ensure all device parameters match"],
)
_register_error(
    "TOOL_NOT_FOUND", "E1001",
    "Required EDA tool was not found.",
    "The tool is not installed or not in the system PATH.",
    ["1. Verify the tool is installed: which <tool-name>",
     "2. Install with: gli-flow install --tool <tool-name>",
     "3. Ensure PATH includes the tool directory"],
)
_register_error(
    "PDK_NOT_FOUND", "E1002",
    "Process design kit (PDK) was not found.",
    "The PDK directory does not exist or is not configured.",
    ["1. Install PDK: gli-flow install --pdk <pdk-name>",
     "2. Set PDK_ROOT environment variable",
     "3. Verify the PDK is compatible with your version"],
)
_register_error(
    "OOM_ERROR", "E1005",
    "Out of memory — the operating system killed a process.",
    "The EDA tool exhausted available system memory.",
    ["1. Increase memory: gli-flow run --memory 32000",
     "2. Reduce design size or core utilization",
     "3. Reduce thread count to lower peak memory"],
)
_register_error(
    "TIMEOUT_ERROR", "E1006",
    "Stage exceeded its time limit and was aborted.",
    "The stage did not complete within the configured timeout.",
    ["1. Increase timeout: gli-flow run --timeout 14400",
     "2. Reduce design complexity",
     "3. Optimize for faster processing time"],
)


def _build_constant(key: str) -> GliFlowError:
    info = _BUILDERS[key]
    return GliFlowError(
        error_code=info["error_code"],
        message=info["message"],
        cause=info["cause"],
        resolution_steps=list(info["resolution_steps"]),
    )


MAGIC_DRC_MISSING: GliFlowError = _build_constant("MAGIC_DRC_MISSING")
LVS_FAILURE: GliFlowError = _build_constant("LVS_FAILURE")
TOOL_NOT_FOUND: GliFlowError = _build_constant("TOOL_NOT_FOUND")
PDK_NOT_FOUND: GliFlowError = _build_constant("PDK_NOT_FOUND")
OOM_ERROR: GliFlowError = _build_constant("OOM_ERROR")
TIMEOUT_ERROR: GliFlowError = _build_constant("TIMEOUT_ERROR")

_ALL_CODES = [
    MAGIC_DRC_MISSING, LVS_FAILURE, TOOL_NOT_FOUND,
    PDK_NOT_FOUND, OOM_ERROR, TIMEOUT_ERROR,
] + [
    GliFlowError(error_code="E1007", message="Config validation error.",
                 cause="Invalid configuration.", resolution_steps=[
                     "1. Validate config: gli-flow validate --config",
                     "2. Check for missing required fields",
                     "3. Refer to configuration schema docs",
                 ]),
    GliFlowError(error_code="E1008", message="Database error.",
                 cause="Corrupt or inaccessible database.", resolution_steps=[
                     "1. Repair DB: gli-flow db repair",
                     "2. Restore from backup: gli-flow db restore",
                     "3. Check disk space and filesystem",
                 ]),
    GliFlowError(error_code="E1009", message="Manifest validation error.",
                 cause="Invalid gli_manifest.yaml.", resolution_steps=[
                     "1. Check syntax: python -c \"import yaml; ...\"",
                     "2. Verify required keys: version, design, stages",
                     "3. Run: gli-flow validate --manifest",
                 ]),
    GliFlowError(error_code="E1010", message="General failure.",
                 cause="An unexpected error occurred.", resolution_steps=[
                     "1. Check full error output above",
                     "2. Run: gli-flow doctor",
                     "3. Report with gli-flow --debug output",
                 ]),
]

ALL_ERROR_CODES: dict[str, GliFlowError] = {
    e.error_code: e for e in _ALL_CODES
}


def format_user_error(error: GliFlowError) -> str:
    """Return a user-friendly error message without raw stack traces."""
    lines = [
        f"[{error.error_code}] {error.message}",
    ]
    if error.cause:
        lines.append(f"  Cause: {error.cause}")
    if error.evidence:
        lines.append(f"  Evidence: {error.evidence}")
    if error.resolution_steps:
        lines.append("  Resolution:")
        for step in error.resolution_steps:
            lines.append(f"    {step}")
    if error.doc_link:
        lines.append(f"  Documentation: {error.doc_link}")
    return "\n".join(lines)


def format_debug_error(error: GliFlowError) -> str:
    """Return a debug-oriented error message that includes traceback info."""
    base = format_user_error(error)
    if error.debug_traceback:
        base += f"\n\nTraceback:\n{error.debug_traceback}"
    return base
