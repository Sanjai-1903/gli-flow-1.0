from typing import List, Optional, Dict, Any


class AIResponse:
    """AI Investigation Assistant response contract.

    STRICT RULES:
    - Never return "Root cause is..."
    - Never return "This will fix it."
    - Instead: "Possible causes", "Suggested investigations"
    """

    def __init__(
        self,
        confidence: str = "LOW",
        summary: str = "",
        possible_causes: Optional[List[str]] = None,
        investigation_steps: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
        disclaimer: bool = True,
    ):
        self.confidence = self._validate_confidence(confidence)
        self.summary = summary
        self.possible_causes = possible_causes or []
        self.investigation_steps = investigation_steps or []
        self.references = references or []
        self.disclaimer = disclaimer

    @staticmethod
    def _validate_confidence(value: str) -> str:
        allowed = {"LOW", "MEDIUM"}
        if value.upper() not in allowed:
            return "LOW"
        return value.upper()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": self.confidence,
            "summary": self.summary,
            "possible_causes": self.possible_causes,
            "investigation_steps": self.investigation_steps,
            "references": self.references,
            "disclaimer": self.disclaimer,
        }

    @classmethod
    def heuristic_fallback(cls, context: Dict[str, Any]) -> "AIResponse":
        """Generate heuristic-based investigation guidance when no LLM is available.
        This is a deterministic fallback that suggests investigations based on
        failure type, tool, and stage — NOT an AI model output.
        """
        failure_type = context.get("failure_type", "")
        tool = context.get("tool", "")
        stage = context.get("stage", "")

        causes = []
        steps = []
        refs = []

        if "SETUP" in failure_type or ("wns" in str(context.get("metrics", {}))):
            causes.append("Clock period may be too aggressive for the current logic depth")
            causes.append("Synthesis may not have optimized critical paths adequately")
            steps.append("Check worst negative slack (WNS) and total negative slack (TNS) in the timing report")
            steps.append("Verify clock constraints in the SDC file match the target frequency")
            steps.append("Try increasing clock period by 20% to isolate timing vs. logic issue")
            steps.append("Run synthesis with higher effort: set 'synth_strategy: DELAY 1' in manifest")
            refs.append("GLI-FLOW Timing Analysis Guide: docs/timing/debugging_setup_violations.md")

        if "HOLD" in failure_type:
            causes.append("Hold fixing may not have run or clock tree may have excessive skew")
            steps.append("Verify 'set_fix_hold' is enabled in the SDC constraints")
            steps.append("Check clock skew report for excessive skew values")
            steps.append("Inspect hold violation endpoints in the STA report")
            refs.append("GLI-FLOW Hold Fixing Guide: docs/timing/hold_violations.md")

        if "DRC" in failure_type or tool.upper() in ("MAGIC", "KLAYOUT"):
            causes.append("Routing may not have completed cleanly — check for unconnected nets")
            causes.append("PDK rule deck may need updating for the target technology")
            steps.append("Open DRC summary and identify the violated rule and coordinates")
            steps.append("Cross-reference DRC violations with routing congestion heatmap")
            steps.append("If violations are at macro boundaries, check pin accessibility")
            refs.append("GLI-FLOW DRC Debug Guide: docs/drc/debugging_drc_violations.md")

        if "LVS" in failure_type:
            causes.append("Power/ground connections may be missing or swapped")
            causes.append("Geometry extraction may have missed a layer due to rule deck settings")
            steps.append("Check LVS report for number of unmatched nets and devices")
            steps.append("Verify power grid (PDN) is properly connected to all standard cells")
            steps.append("Run LVS with flat extraction to rule out hierarchical issues")
            refs.append("GLI-FLOW LVS Debug Guide: docs/lvs/debugging_lvs_mismatch.md")

        if tool.upper() == "OPENROAD" and "OOM" in failure_type.upper():
            causes.append("Design may be too large for available system memory")
            steps.append("Check system memory usage during the failing stage")
            steps.append("Try reducing thread count to lower memory pressure")
            steps.append("Enable hierarchical flow to partition the design")
            refs.append("GLI-FLOW OOM Troubleshooting: docs/runtime/out_of_memory.md")

        if tool.upper() in ("MAGIC", "NETGEN") and not causes:
            causes.append("Tool may not have the correct PDK configuration or technology file")
            causes.append("Wrapper script may have a path shadowing issue")
            steps.append("Run 'gli-flow doctor' to check tool and PDK health")
            steps.append("Verify the technology file (.tech) is present and corresponds to the target PDK")
            refs.append("GLI-FLOW Infrastructure Guide: docs/infrastructure/tool_configuration.md")

        if not causes:
            causes.append("Failure type does not match common patterns — manual log inspection recommended")
            steps.append("Examine the full log file for unrecognized error messages")
            steps.append("Search the error text in the GLI-FLOW issue tracker or community forum")
            steps.append("Run a known-good example (e.g., 'examples/gcd') to isolate environment vs. design issue")
            refs.append("GLI-FLOW Failure Atlas: failure_atlas/README.md")

        steps.append("If the issue persists, file a report with the full telemetry and log files")

        return cls(
            confidence="LOW",
            summary=f"Heuristic investigation guidance for {failure_type} failure at {stage} stage",
            possible_causes=causes,
            investigation_steps=steps,
            references=refs,
            disclaimer=True,
        )


def validate_response(data: Dict[str, Any]) -> List[str]:
    """Validate a response dict against the AI response contract.
    Returns a list of validation errors (empty = valid).
    """
    errors = []

    if not isinstance(data, dict):
        return ["Response must be a JSON object"]

    confidence = data.get("confidence", "LOW")
    allowed = {"LOW", "MEDIUM"}
    if confidence.upper() not in allowed:
        errors.append(f"confidence must be one of {allowed}, got {confidence}")

    for field in ("summary",):
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for field in ("possible_causes", "investigation_steps", "references"):
        val = data.get(field, [])
        if not isinstance(val, list):
            errors.append(f"{field} must be a list")
        elif len(val) > 50:
            errors.append(f"{field} exceeds maximum of 50 items")

    summary = data.get("summary", "")
    root_cause_phrases = [
        "root cause is",
        "the root cause",
        "this will fix",
        "definitely caused by",
        "guaranteed to resolve",
    ]
    summary_lower = summary.lower()
    for phrase in root_cause_phrases:
        if phrase in summary_lower:
            errors.append(f"Summary must not claim root cause: contains '{phrase}'")

    for cause in data.get("possible_causes", []):
        cause_lower = cause.lower()
        for phrase in root_cause_phrases:
            if phrase in cause_lower:
                errors.append(f"Possible cause must not claim root cause: contains '{phrase}'")
                break

    if not data.get("disclaimer", False):
        errors.append("disclaimer must be true")

    return errors
