"""GLI-FLOW domain exceptions."""


class GLIFlowError(Exception):
    """Base class for all GLI-FLOW errors."""
    pass


class StageOOMError(GLIFlowError):
    """EDA tool was killed by OOM killer."""
    def __init__(self, stage: str,
                 memory_limit_mb: int = None):
        self.stage = stage
        self.memory_limit_mb = memory_limit_mb
        hint = (
            f" (limit was {memory_limit_mb}MB)"
            if memory_limit_mb else ""
        )
        super().__init__(
            f"Stage '{stage}' was killed by the OS "
            f"out-of-memory killer{hint}.\n"
            f"Fix options:\n"
            f"  1. Reduce design size or core utilization\n"
            f"  2. Increase available RAM\n"
            f"  3. Run: gli-flow run <design> --memory 32000 to request more memory\n"
            f"  4. Reduce --threads to free memory"
        )


class StageTimeoutError(GLIFlowError):
    """EDA tool exceeded time limit."""
    def __init__(self, stage: str,
                 timeout_seconds: int):
        super().__init__(
            f"Stage '{stage}' timed out after "
            f"{timeout_seconds // 60} minutes.\n"
            f"Fix options:\n"
            f"  1. Increase timeout: gli-flow run <design> --timeout 14400\n"
            f"  2. Reduce design complexity\n"
            f"  3. Reduce core utilization in manifest"
        )


class ManifestValidationError(GLIFlowError):
    """gli_manifest.yaml is invalid."""
    pass


class ToolNotFoundError(GLIFlowError):
    """Required EDA tool not installed."""
    def __init__(self, tool: str):
        super().__init__(
            f"Required tool '{tool}' not found.\n"
            f"Fix: gli-flow install --pdk sky130\n"
            f"Or check installation with: gli-flow doctor"
        )


class PDKNotFoundError(GLIFlowError):
    """PDK root directory not found."""
    def __init__(self, pdk: str,
                 searched_paths: list = None):
        paths = (
            "\n  Searched: " + "\n           ".join(searched_paths)
            if searched_paths else ""
        )
        super().__init__(
            f"PDK '{pdk}' not found.{paths}\n"
            f"Fix: Set PDK_ROOT environment variable to your PDK directory.\n"
            f"Or install: gli-flow install --pdk "
            f"{pdk.replace('A','').lower()}"
        )


class SynthesisSafetyError(GLIFlowError):
    """Synthesis safety check failed — blocks tapeout."""
    def __init__(self, check: str, detail: str, fix: str):
        super().__init__(
            f"TAPEOUT BLOCKER — {check}\n"
            f"Detail: {detail}\n"
            f"Fix: {fix}"
        )


class RoutingOverflowError(GLIFlowError):
    """Global routing overflow too high to complete."""
    def __init__(self, overflow_pct: float):
        super().__init__(
            f"Global routing overflow {overflow_pct:.1%} exceeds 5% threshold.\n"
            f"Routing will not complete. Failing fast instead of waiting hours.\n"
            f"Fix options:\n"
            f"  1. Reduce FP_CORE_UTIL by at least 15% in gli_manifest.yaml\n"
            f"  2. Increase die area\n"
            f"  3. Reduce design complexity\n"
            f"  Related: Failure Atlas FA-0002"
        )


class TapeoutBlockingError(GLIFlowError):
    """A signoff check failed that blocks tapeout."""
    pass


class StageFailure(GLIFlowError):
    """A specific stage in the flow failed."""
    pass


class DRCReportMissingError(StageFailure):
    """DRC report is missing - treated as failure, not clean."""
    pass


class DRCReportUnparseable(StageFailure):
    """DRC report format not recognized."""
    pass
