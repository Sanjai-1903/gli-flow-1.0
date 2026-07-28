from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CIReport:
    success: bool
    run_id: str
    design_name: str
    metrics: dict
    baseline_metrics: Optional[dict]
    regressions: list[str]
    duration: float
    error: Optional[str] = None


def generate_junit_xml(report: CIReport) -> str:
    testsuite = ET.Element("testsuite", {
        "name": f"gli-flow.{report.design_name}",
        "tests": "1",
        "failures": "0" if report.success else "1",
        "errors": "0",
        "time": f"{report.duration:.2f}",
    })

    props = ET.SubElement(testsuite, "properties")
    for key, value in report.metrics.items():
        if value is not None:
            ET.SubElement(props, "property", {"name": key, "value": str(value)})

    if report.baseline_metrics:
        for key, value in report.baseline_metrics.items():
            if value is not None:
                ET.SubElement(props, "property", {"name": f"baseline_{key}", "value": str(value)})

    testcase = ET.SubElement(testsuite, "testcase", {
        "classname": f"gli-flow.{report.design_name}",
        "name": report.run_id,
        "time": f"{report.duration:.2f}",
    })

    if report.regressions:
        failure_msg = "\n".join(report.regressions)
        ET.SubElement(testcase, "failure", {"message": failure_msg, "type": "regression"})

    if report.error:
        ET.SubElement(testcase, "error", {"message": report.error})

    system_out = ET.SubElement(testsuite, "system-out")
    system_out.text = (
        f"Design: {report.design_name}\n"
        f"Run ID: {report.run_id}\n"
        f"Metrics: {report.metrics}\n"
    )

    return ET.tostring(testsuite, encoding="unicode")


def generate_markdown_report(report: CIReport) -> str:
    lines = []
    lines.append(f"# CI Report: {report.design_name}")
    lines.append("")
    lines.append(f"**Run ID:** `{report.run_id}`")
    lines.append(f"**Status:** {'✅ PASS' if report.success else '❌ FAIL'}")
    lines.append(f"**Duration:** {report.duration:.1f}s")
    lines.append("")

    if report.metrics:
        lines.append("## Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        for key, value in sorted(report.metrics.items()):
            if value is not None:
                lines.append(f"| {key} | {value} |")
        lines.append("")

    if report.baseline_metrics:
        lines.append("## Baseline Comparison")
        lines.append("")
        lines.append("| Metric | Current | Baseline | Delta |")
        lines.append("|--------|---------|----------|-------|")
        for key in sorted(set(list(report.metrics.keys()) + list(report.baseline_metrics.keys()))):
            cur = report.metrics.get(key)
            bl = report.baseline_metrics.get(key)
            if cur is not None and bl is not None:
                delta = cur - bl
                delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
                lines.append(f"| {key} | {cur} | {bl} | {delta_str} |")
        lines.append("")

    if report.regressions:
        lines.append("## Regressions Detected")
        lines.append("")
        for r in report.regressions:
            lines.append(f"- ⚠️ {r}")
        lines.append("")

    if report.error:
        lines.append(f"## Error\n\n{report.error}\n")

    return "\n".join(lines)
