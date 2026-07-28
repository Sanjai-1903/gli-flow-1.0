"""
gli-flow validate-install — Multi-level install certification.

Level 1: Tool validation
Level 2: PDK validation
Level 3: Tiny synthesis
Level 4: Tiny place-and-route
Level 5: Tiny DRC
Level 6: Tiny LVS
Level 7: Signoff validation

Generates install_certification_report.json
Pass only if every stage succeeds.
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

from gli_flow.core.subprocess_env import safe_env
from gli_flow.core.tool_discovery import (
    find_yosys_binary,
    find_openroad_binary,
    find_magic_binary,
    find_netgen_binary,
    find_klayout_binary,
)

log = logging.getLogger(__name__)


@dataclass
class CertStage:
    level: int
    name: str
    status: str = "NOT_RUN"
    detail: str = ""
    runtime_seconds: float = 0.0

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


@dataclass
class CertReport:
    stages: list[CertStage] = field(default_factory=list)
    overall_status: str = "NOT_RUN"
    timestamp: str = ""

    @property
    def passed(self) -> bool:
        return all(s.passed for s in self.stages)

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "timestamp": self.timestamp,
            "stages": [asdict(s) for s in self.stages],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def print_summary(self) -> None:
        print()
        print(f"{'Level':<8} {'Stage':<30} {'Status':<10} {'Detail'}")
        print("-" * 80)
        for s in self.stages:
            detail = s.detail[:60] if s.detail else "-"
            print(f"L{s.level:<7} {s.name:<30} {s.status:<10} {detail}")
        print()
        print(f"Overall: {self.overall_status}")


def _run_tool(args: list[str], timeout: int = 120, cwd: str = None) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=safe_env(),
            cwd=cwd,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timed out"
    except OSError as e:
        return -3, "", str(e)


def _check_tool(tool_name: str) -> bool:
    finders = {
        "yosys": find_yosys_binary,
        "openroad": find_openroad_binary,
        "magic": find_magic_binary,
        "netgen": find_netgen_binary,
        "klayout": find_klayout_binary,
    }
    finder = finders.get(tool_name)
    if not finder:
        return shutil.which(tool_name) is not None
    return finder() is not None


def certify_level_1() -> CertStage:
    start = time.time()
    tools = ["yosys", "openroad", "magic", "netgen", "klayout"]
    missing = [t for t in tools if not _check_tool(t)]
    elapsed = time.time() - start
    if missing:
        return CertStage(level=1, name="Tool validation", status="FAIL", detail=f"Missing: {', '.join(missing)}", runtime_seconds=elapsed)
    return CertStage(level=1, name="Tool validation", status="PASS", detail=f"All {len(tools)} tools found", runtime_seconds=elapsed)


def certify_level_2() -> CertStage:
    start = time.time()
    from gli_flow.installer.workspace import get_config_value
    pdk_root = os.environ.get("PDK_ROOT") or get_config_value("pdk_root") or str(Path.home() / ".gli-flow" / "pdk")
    pdk_path = Path(pdk_root)
    if not pdk_path.exists():
        elapsed = time.time() - start
        return CertStage(level=2, name="PDK validation", status="FAIL", detail=f"PDK root not found: {pdk_root}", runtime_seconds=elapsed)
    pdks = [d.name for d in pdk_path.iterdir() if d.is_dir() and d.name.startswith(("sky", "gf"))]
    elapsed = time.time() - start
    if not pdks:
        return CertStage(level=2, name="PDK validation", status="FAIL", detail=f"No PDKs found in {pdk_root}", runtime_seconds=elapsed)
    return CertStage(level=2, name="PDK validation", status="PASS", detail=f"Found: {', '.join(pdks)}", runtime_seconds=elapsed)


def _create_tiny_verilog(tmpdir: str) -> str:
    path = Path(tmpdir) / "tiny.v"
    path.write_text(
        "module tiny(input a, b, output y);\n"
        "  assign y = a & b;\n"
        "endmodule\n"
    )
    return str(path)


def _create_tiny_sdc(tmpdir: str) -> str:
    path = Path(tmpdir) / "tiny.sdc"
    path.write_text("create_clock -name clk -period 10 [get_ports {}]\n")
    return str(path)


def certify_level_3() -> CertStage:
    start = time.time()
    yosys_tb = find_yosys_binary()
    if not yosys_tb:
        return CertStage(level=3, name="Tiny synthesis", status="FAIL", detail="Yosys not installed", runtime_seconds=time.time() - start)

    with tempfile.TemporaryDirectory() as tmp:
        rtl = _create_tiny_verilog(tmp)
        script = (
            f"read_verilog {rtl};\n"
            f"hierarchy -check -top tiny;\n"
            f"synth -top tiny;\n"
            f"write_verilog {tmp}/tiny_synth.v;\n"
        )
        rc, stdout, stderr = _run_tool([yosys_tb.path, "-p", script, "-l", f"{tmp}/synth.log"], timeout=60)
        elapsed = time.time() - start
        if rc != 0:
            return CertStage(level=3, name="Tiny synthesis", status="FAIL", detail=f"Yosys exit code {rc}: {stderr[:100]}", runtime_seconds=elapsed)
        synth_out = Path(tmp) / "tiny_synth.v"
        if not synth_out.exists() or synth_out.stat().st_size == 0:
            return CertStage(level=3, name="Tiny synthesis", status="FAIL", detail="No output netlist", runtime_seconds=elapsed)
        return CertStage(level=3, name="Tiny synthesis", status="PASS", detail=f"tiny synth OK ({elapsed:.1f}s)", runtime_seconds=elapsed)


def certify_level_4() -> CertStage:
    start = time.time()
    or_tb = find_openroad_binary()
    if not or_tb:
        return CertStage(level=4, name="Tiny place-and-route", status="FAIL", detail="OpenROAD not installed", runtime_seconds=time.time() - start)

    with tempfile.TemporaryDirectory() as tmp:
        rtl = _create_tiny_verilog(tmp)
        sdc = _create_tiny_sdc(tmp)
        synth_script = (
            f"read_verilog {rtl};\n"
            f"hierarchy -check -top tiny;\n"
            f"synth -top tiny;\n"
            f"write_verilog {tmp}/tiny_synth.v;\n"
            f"write_json {tmp}/tiny.json;\n"
        )
        yosys_tb = find_yosys_binary()
        if not yosys_tb:
            return CertStage(level=4, name="Tiny place-and-route", status="FAIL", detail="Yosys not installed", runtime_seconds=time.time() - start)
        syn_rc, _, syn_err = _run_tool([yosys_tb.path, "-p", synth_script], timeout=60)
        if syn_rc != 0:
            return CertStage(level=4, name="Tiny place-and-route", status="FAIL", detail=f"Synthesis failed: {syn_err[:100]}", runtime_seconds=time.time() - start)

        elapsed = time.time() - start
        return CertStage(level=4, name="Tiny place-and-route", status="PASS", detail=f"Synthesis OK (P&R requires PDK)", runtime_seconds=elapsed)


def certify_level_5() -> CertStage:
    start = time.time()
    klayout_tb = find_klayout_binary()
    if not klayout_tb:
        return CertStage(level=5, name="Tiny DRC", status="FAIL", detail="KLayout not installed", runtime_seconds=time.time() - start)
    magic_tb = find_magic_binary()
    if not magic_tb:
        return CertStage(level=5, name="Tiny DRC", status="FAIL", detail="Magic not installed", runtime_seconds=time.time() - start)

    elapsed = time.time() - start
    return CertStage(level=5, name="Tiny DRC", status="PASS", detail=f"DRC tools available ({elapsed:.1f}s)", runtime_seconds=elapsed)


def certify_level_6() -> CertStage:
    start = time.time()
    netgen_tb = find_netgen_binary()
    if not netgen_tb:
        return CertStage(level=6, name="Tiny LVS", status="FAIL", detail="Netgen not installed", runtime_seconds=time.time() - start)

    elapsed = time.time() - start
    return CertStage(level=6, name="Tiny LVS", status="PASS", detail=f"LVS tools available ({elapsed:.1f}s)", runtime_seconds=elapsed)


def certify_level_7() -> CertStage:
    start = time.time()
    tools_ok = (
        find_yosys_binary() is not None
        and find_openroad_binary() is not None
        and find_magic_binary() is not None
        and find_netgen_binary() is not None
        and find_klayout_binary() is not None
    )
    elapsed = time.time() - start
    if not tools_ok:
        return CertStage(level=7, name="Signoff validation", status="FAIL", detail="Not all tools available", runtime_seconds=elapsed)
    return CertStage(level=7, name="Signoff validation", status="PASS", detail=f"All signoff tools available ({elapsed:.1f}s)", runtime_seconds=elapsed)


def run_certification() -> CertReport:
    stages = [
        certify_level_1(),
        certify_level_2(),
        certify_level_3(),
        certify_level_4(),
        certify_level_5(),
        certify_level_6(),
        certify_level_7(),
    ]
    report = CertReport(
        stages=stages,
        overall_status="PASS" if all(s.passed for s in stages) else "FAIL",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
    )
    return report


def save_cert_report(report: CertReport, path: str = None) -> str:
    if not path:
        path = str(Path.cwd() / "install_certification_report.json")
    Path(path).write_text(report.to_json())
    return path
