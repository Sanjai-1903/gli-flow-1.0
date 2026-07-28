import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from gli_flow.core.subprocess_env import safe_env

# Single source of truth for search paths
from gli_flow.core.tool_discovery import EXTRA_PATH_DIRS as CORE_EXTRA_PATH_DIRS, is_broken_version, find_magicdnull_binary


class Confidence(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


@dataclass
class DetectionMethod:
    name: str
    weight: int = 1


@dataclass
class DetectionResult:
    tool: str
    exists: bool = False
    path: Optional[str] = None
    version: Optional[str] = None
    version_raw: Optional[str] = None
    confidence: Confidence = Confidence.UNKNOWN
    methods_tried: list[str] = field(default_factory=list)
    methods_succeeded: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    detail: str = ""

    @property
    def score(self) -> float:
        if self.confidence == Confidence.HIGH:
            return 1.0
        if self.confidence == Confidence.MEDIUM:
            return 0.6
        if self.confidence == Confidence.LOW:
            return 0.3
        return 0.0


def _run_cmd(args: list[str], timeout: int = 5) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=safe_env(),
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timed out"
    except OSError as e:
        return -3, "", str(e)


_VERSION_PARSE_CACHE: dict[str, tuple[int, ...]] = {}


def _parse_semver(text: str) -> tuple[int, ...]:
    if text in _VERSION_PARSE_CACHE:
        return _VERSION_PARSE_CACHE[text]
    digits = re.findall(r"(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)", text)
    if digits:
        parts = digits[0].split(".")
        result = tuple(int(p) for p in parts)
    else:
        single = re.findall(r"(\d+)", text)
        if single:
            result = (int(single[0]),)
        else:
            result = (0,)
    _VERSION_PARSE_CACHE[text] = result
    return result


def parse_version(text: str) -> tuple[int, ...]:
    return _parse_semver(text)


def meets_min_version(version_str: Optional[str], minimum: str) -> bool:
    if not version_str:
        return False
    try:
        return _parse_semver(version_str) >= _parse_semver(minimum)
    except Exception:
        return False


EXTRA_PATH_DIRS = [
    "/usr/local/bin",
    "<HOME>/.local/bin",
    "<HOME>/.gli-flow/tools/bin",
    "<HOME>/.gli-flow/orfs/tools/install/OpenROAD/bin",
    "<HOME>/.gli-flow/orfs/tools/install/Yosys/bin",
    "/pdk",
    "/usr/lib/netgen",
    "/usr/local/lib/netgen",
]


def _resolve_home_path(path: str) -> str:
    """Resolve HOME_PREFIX to actual home directory at call time."""
    if path.startswith("<HOME>"):
        return str(Path.home() / path[len("<HOME>/"):])
    return path


def _find_on_path(name: str) -> Optional[str]:
    path = shutil.which(name)
    if path:
        return path
    # Check local extra dirs first
    for extra in EXTRA_PATH_DIRS:
        candidate = Path(_resolve_home_path(extra)) / name
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate)
    # Fall through to core discovery search paths (resolved at call time)
    for extra in CORE_EXTRA_PATH_DIRS:
        candidate = Path(_resolve_home_path(extra)) / name
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate)
    return None


MethodFn = Callable[[], Optional[str]]


class ToolDetector:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.results: list[DetectionResult] = []
        self._combined: Optional[DetectionResult] = None

    def add_method(self, name: str, fn: MethodFn) -> "ToolDetector":
        try:
            result = fn()
        except Exception as e:
            result = None
        dr = DetectionResult(tool=self.tool_name)
        dr.methods_tried.append(name)
        if result:
            dr.exists = True
            dr.path = result
            dr.methods_succeeded.append(name)
            dr.confidence = Confidence.LOW
        else:
            dr.errors.append(f"{name}: no result")
        self.results.append(dr)
        return self

    def add_version_method(self, name: str, args: list[str], parser: Optional[Callable[[str], Optional[str]]] = None) -> "ToolDetector":
        dr = DetectionResult(tool=self.tool_name)
        dr.methods_tried.append(name)
        rc, stdout, stderr = _run_cmd(args)
        if rc == 0 and (stdout.strip() or stderr.strip()):
            raw = (stdout or stderr).strip()
            dr.exists = True
            dr.path = shutil.which(args[0]) or _find_on_path(args[0])
            dr.version_raw = raw.split("\n")[0]
            if parser:
                dr.version = parser(raw)
            else:
                dr.version = dr.version_raw
            dr.methods_succeeded.append(name)
            dr.confidence = Confidence.HIGH if rc == 0 else Confidence.MEDIUM
        else:
            err = stderr.strip() or stdout.strip() or f"exit code {rc}"
            dr.errors.append(f"{name}: {err}")
        self.results.append(dr)
        return self

    def combine(self) -> DetectionResult:
        if self._combined:
            return self._combined
        best = DetectionResult(tool=self.tool_name)
        for r in self.results:
            best.methods_tried.extend(r.methods_tried)
            best.methods_succeeded.extend(r.methods_succeeded)
            best.errors.extend(r.errors)
            if r.exists and r.path and (best.path is None or r.score > best.score):
                best.exists = True
                best.path = r.path
                best.version = r.version
                best.version_raw = r.version_raw
                best.confidence = r.confidence
        if not best.exists:
            for r in self.results:
                if r.exists:
                    best.exists = True
                    best.path = r.path
                    best.confidence = r.confidence
                    break
        if not best.exists:
            best.confidence = Confidence.UNKNOWN
            best.detail = f"'{self.tool_name}' not found"
        elif best.confidence == Confidence.LOW:
            best.detail = f"'{self.tool_name}' detected at {best.path} but version could not be parsed"
        elif best.version:
            best.detail = f"'{self.tool_name}' {best.version} at {best.path}"
        else:
            best.detail = f"'{self.tool_name}' at {best.path}"
        self._combined = best
        return best

    def detect(self) -> DetectionResult:
        return self.combine()


def detect_magic() -> DetectionResult:
    return (
        ToolDetector("magic")
        .add_method("which magic", lambda: _find_on_path("magic"))
        .add_method("/usr/bin/magic", lambda: "/usr/bin/magic" if os.path.exists("/usr/bin/magic") else None)
        .add_version_method("magic --version", ["magic", "--version"])
        .add_version_method("/usr/bin/magic --version", ["/usr/bin/magic", "--version"])
        .add_version_method("magic -version", ["magic", "-version"])
        .add_version_method("magic -noconsole -dnull -version", ["magic", "-noconsole", "-dnull", "-version"])
        .combine()
    )


def _parse_netgen_version(raw: str) -> Optional[str]:
    m = re.search(r'[Nn]etgen\s+(\d+\.\d+(?:\.\d+)?)', raw)
    if m:
        return m.group(1)
    return None


def detect_magicdnull() -> DetectionResult:
    result = DetectionResult(tool="magicdnull")
    tb = find_magicdnull_binary()
    if tb:
        result.exists = True
        result.path = tb.path
        result.version = tb.version_str
        result.confidence = Confidence.HIGH
        result.detail = f"'magicdnull' {tb.version_str} at {tb.path}"
    else:
        result.detail = "'magicdnull' not found"
    return result


def detect_netgen() -> DetectionResult:
    return (
        ToolDetector("netgen")
        .add_method("which netgen-lvs", lambda: _find_on_path("netgen-lvs"))
        .add_method("/usr/bin/netgen-lvs", lambda: "/usr/bin/netgen-lvs" if os.path.exists("/usr/bin/netgen-lvs") else None)
        .add_method("/usr/lib/netgen/bin/netgen", lambda: "/usr/lib/netgen/bin/netgen" if os.path.exists("/usr/lib/netgen/bin/netgen") else None)
        .add_method("which netgen", lambda: _find_on_path("netgen"))
        .add_method("which netgenexec", lambda: _find_on_path("netgenexec"))
        .add_version_method("netgen-lvs -batch quit", ["netgen-lvs", "-batch", "quit"], parser=_parse_netgen_version)
        .add_version_method("/usr/bin/netgen-lvs -batch quit", ["/usr/bin/netgen-lvs", "-batch", "quit"], parser=_parse_netgen_version)
        .add_version_method("/usr/lib/netgen/bin/netgen -batch quit", ["/usr/lib/netgen/bin/netgen", "-batch", "quit"], parser=_parse_netgen_version)
        .add_version_method("netgen -batch quit", ["netgen", "-batch", "quit"], parser=_parse_netgen_version)
        .combine()
    )


def detect_yosys() -> DetectionResult:
    return (
        ToolDetector("yosys")
        .add_method("which yosys", lambda: _find_on_path("yosys"))
        .add_version_method("yosys -V", ["yosys", "-V"])
        .add_version_method("yosys --version", ["yosys", "--version"])
        .combine()
    )


def detect_openroad() -> DetectionResult:
    return (
        ToolDetector("openroad")
        .add_method("which openroad", lambda: _find_on_path("openroad"))
        .add_version_method("openroad -version", ["openroad", "-version"])
        .combine()
    )


def detect_klayout() -> DetectionResult:
    return (
        ToolDetector("klayout")
        .add_method("which klayout", lambda: _find_on_path("klayout"))
        .add_version_method("klayout -b -v", ["klayout", "-b", "-v"])
        .combine()
    )


def detect_sv2v() -> DetectionResult:
    return (
        ToolDetector("sv2v")
        .add_method("which sv2v", lambda: _find_on_path("sv2v"))
        .add_version_method("sv2v --version", ["sv2v", "--version"])
        .combine()
    )


def detect_git() -> DetectionResult:
    return (
        ToolDetector("git")
        .add_method("which git", lambda: _find_on_path("git"))
        .add_version_method("git --version", ["git", "--version"])
        .combine()
    )


def detect_cmake() -> DetectionResult:
    return (
        ToolDetector("cmake")
        .add_method("which cmake", lambda: _find_on_path("cmake"))
        .add_version_method("cmake --version", ["cmake", "--version"])
        .combine()
    )


def detect_python3() -> DetectionResult:
    import platform as _platform
    r = (
        ToolDetector("python3")
        .add_method("which python3", lambda: _find_on_path("python3"))
        .combine()
    )
    ver = _platform.python_version()
    r.version = ver
    r.confidence = Confidence.HIGH
    return r


TOOL_DETECTORS: dict[str, Callable[[], DetectionResult]] = {
    "magic": detect_magic,
    "netgen": detect_netgen,
    "yosys": detect_yosys,
    "openroad": detect_openroad,
    "klayout": detect_klayout,
    "sv2v": detect_sv2v,
    "git": detect_git,
    "cmake": detect_cmake,
    "python3": detect_python3,
}


def detect_tool(name: str) -> DetectionResult:
    detector = TOOL_DETECTORS.get(name)
    if detector:
        return detector()
    basic = ToolDetector(name)
    basic.add_method(f"which {name}", lambda: _find_on_path(name))
    basic.add_version_method(f"{name} --version", [name, "--version"])
    return basic.combine()


def detect_netgen_lib_dir() -> Optional[str]:
    candidates = [
        "/usr/lib/netgen",
        "/usr/local/lib/netgen",
        "/usr/lib/x86_64-linux-gnu/netgen",
        str(Path.home() / ".gli-flow" / "tools" / "lib" / "netgen"),
    ]
    for d in candidates:
        p = Path(d)
        if p.is_dir():
            for f in p.iterdir():
                if "tclnetgen" in f.name and f.suffix in (".so", ".dylib"):
                    return str(d)
    for root in ["/usr/lib", "/usr/local/lib", str(Path.home() / ".gli-flow")]:
        p = Path(root)
        if p.is_dir():
            for f in p.rglob("tclnetgen*"):
                if f.suffix in (".so", ".dylib"):
                    return str(f.parent)
    return None


def detect_netgenexec() -> Optional[str]:
    return _find_on_path("netgenexec") or _find_on_path("netgen-lvs")
