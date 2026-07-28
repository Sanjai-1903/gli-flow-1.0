import csv
import json
import os
import re

from pathlib import Path


class TelemetryParser:

    def __init__(self, reports_dir, run_dir=None):
        self.reports_dir = Path(reports_dir)
        self.run_dir = Path(run_dir) if run_dir else None

    def _safe_read_lines(self, path):
        try:
            with open(path, "r") as f:
                return f.readlines()
        except (FileNotFoundError, OSError):
            return []

    def _parse_key_value_lines(self, lines, separators=(":",)):
        metrics = {}
        for line in lines:
            for sep in separators:
                if sep in line:
                    parts = line.split(sep, 1)
                    key = parts[0].strip()
                    raw = parts[1].strip()
                    try:
                        value = float(raw.replace("%", "").replace("sec", "").strip())
                        metrics[key.lower().replace(" ", "_")] = value
                    except ValueError:
                        try:
                            value = int(raw)
                            metrics[key.lower().replace(" ", "_")] = value
                        except ValueError:
                            pass
                    break
        return metrics

    def _parse_csv(self, path):
        metrics = {}
        try:
            with open(path, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        key = row[0].strip().lower().replace(" ", "_")
                        raw = row[1].strip()
                        try:
                            metrics[key] = float(raw)
                        except ValueError:
                            try:
                                metrics[key] = int(raw)
                            except ValueError:
                                pass
        except (FileNotFoundError, OSError):
            pass
        return metrics

    def parse_timing(self):
        metrics = {}
        metrics["timing_unit"] = "ns"

        csv_path = self.reports_dir / "metrics.csv"
        if csv_path.exists():
            parsed = self._parse_csv(csv_path)
            if "wns" in parsed:
                metrics["setup_wns_ns"] = parsed["wns"]
            if "tns" in parsed:
                metrics["setup_tns_ns"] = parsed["tns"]
            if "hold_whs" in parsed:
                metrics["hold_whs_ns"] = parsed["hold_whs"]
            if "hold_ths" in parsed:
                metrics["hold_ths_ns"] = parsed["hold_ths"]

        hold_patterns = [
            (r"whs\s+([-\d.]+)", "hold_whs_ns"),
            (r"ths\s+([-\d.]+)", "hold_ths_ns"),
            (r"Worst Hold Slack.*?:\s*([-\d.]+)", "hold_whs_ns"),
            (r"Total Hold Slack.*?:\s*([-\d.]+)", "hold_ths_ns"),
            (r"timing__hold__ws\s+([-\d.]+)", "hold_whs_ns"),
            (r"timing__hold__tns\s+([-\d.]+)", "hold_ths_ns"),
        ]

        timing_file = self.reports_dir / "timing.rpt"
        if timing_file.exists():
            lines = self._safe_read_lines(timing_file)
            parsed = self._parse_key_value_lines(lines)
            key_map = {"wns": "setup_wns_ns", "tns": "setup_tns_ns"}
            for k, v in parsed.items():
                if k in key_map:
                    metrics[key_map[k]] = v

            content = "".join(lines)
            for pattern, key in hold_patterns:
                m = re.search(pattern, content, re.IGNORECASE)
                if m and key not in metrics:
                    metrics[key] = float(m.group(1))

            hold_vio = re.search(
                r"timing__hold__p_vios\s+(\d+)|"
                r"(\d+)\s+hold\s+violation",
                content, re.IGNORECASE
            )
            if hold_vio:
                metrics["hold_failing_endpoints"] = int(
                    hold_vio.group(1) or hold_vio.group(2)
                )

        metrics_file = self.reports_dir / "metrics.rpt"
        if metrics_file.exists():
            lines = self._safe_read_lines(metrics_file)
            parsed = self._parse_key_value_lines(lines)
            if "setup_wns_ns" not in metrics and "wns" in parsed:
                metrics["setup_wns_ns"] = parsed["wns"]
            if "setup_tns_ns" not in metrics and "tns" in parsed:
                metrics["setup_tns_ns"] = parsed["tns"]

            content = "".join(lines)
            for pattern, key in hold_patterns:
                m = re.search(pattern, content, re.IGNORECASE)
                if m and key not in metrics:
                    metrics[key] = float(m.group(1))

            hold_vio = re.search(
                r"timing__hold__p_vios\s+(\d+)|"
                r"(\d+)\s+hold\s+violation",
                content, re.IGNORECASE
            )
            if hold_vio:
                metrics.setdefault("hold_failing_endpoints", int(
                    hold_vio.group(1) or hold_vio.group(2)
                ))

        setup_wns = metrics.get("setup_wns_ns")
        sta_setup = "PASS" if (setup_wns is not None and setup_wns >= 0) else ("NOT_RUN" if setup_wns is None else "FAIL")
        metrics["sta_setup_status"] = sta_setup
        hold_whs = metrics.get("hold_whs_ns")
        sta_hold = "PASS" if (hold_whs is not None and hold_whs >= 0) else ("NOT_RUN" if hold_whs is None else "FAIL")
        metrics["sta_hold_status"] = sta_hold

        if sta_setup == "NOT_RUN" and sta_hold == "NOT_RUN":
            metrics["timing_status"] = "NOT_RUN"
        elif sta_setup == "FAIL" or sta_hold == "FAIL":
            metrics["timing_status"] = "FAIL"
        else:
            metrics["timing_status"] = "PASS"

        return metrics

    def parse_utilization(self):
        metrics = {}

        csv_path = self.reports_dir / "metrics.csv"
        if csv_path.exists():
            parsed = self._parse_csv(csv_path)
            if "utilization" in parsed:
                metrics["utilization"] = parsed["utilization"]
            if "cell_count" in parsed:
                metrics["cell_count"] = int(parsed["cell_count"])

        util_file = self.reports_dir / "utilization.rpt"
        if util_file.exists():
            lines = self._safe_read_lines(util_file)
            for line in lines:
                if "Core Utilization:" in line:
                    try:
                        value = float(line.split(":")[1].replace("%", "").strip())
                        metrics["utilization"] = value
                    except (ValueError, IndexError):
                        pass
                if "Total Cells:" in line:
                    try:
                        metrics["cell_count"] = int(line.split(":")[1].strip())
                    except (ValueError, IndexError):
                        pass

        metrics_file = self.reports_dir / "metrics.rpt"
        if metrics_file.exists():
            lines = self._safe_read_lines(metrics_file)
            for line in lines:
                if "utilization" not in metrics and "Utilization:" in line:
                    try:
                        value = float(line.split(":")[1].replace("%", "").strip())
                        metrics["utilization"] = value
                    except (ValueError, IndexError):
                        pass
                if "cell_count" not in metrics and "Total Cells:" in line:
                    try:
                        metrics["cell_count"] = int(line.split(":")[1].strip())
                    except (ValueError, IndexError):
                        pass

        return metrics

    def parse_runtime(self):
        metrics = {}

        csv_path = self.reports_dir / "metrics.csv"
        if csv_path.exists():
            parsed = self._parse_csv(csv_path)
            if "runtime_sec" in parsed:
                metrics["runtime_sec"] = parsed["runtime_sec"]

        runtime_file = self.reports_dir / "runtime.rpt"
        if runtime_file.exists():
            lines = self._safe_read_lines(runtime_file)
            for line in lines:
                if "Total Runtime:" in line:
                    try:
                        value = float(line.split(":")[1].replace("sec", "").strip())
                        metrics["runtime_sec"] = value
                    except (ValueError, IndexError):
                        pass

        return metrics

    def parse_drc_combined_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            return {}
        total = data.get("total_violations", 0)
        status = "PASS" if total == 0 else "FAIL"
        is_clean = total == 0
        result = {
            "drc_status": data.get("drc_status", status),
            "drc_total_violations": total,
            "drc_is_clean": is_clean,
            "drc_runtime_seconds": data.get("runtime_seconds"),
        }
        if "magic" in data:
            mg = data["magic"]
            result["drc_magic_violations"] = mg.get("violations", 0)
            result["drc_magic_status"] = "PASS" if mg.get("violations", 0) == 0 else "FAIL"
        if "klayout" in data:
            kl = data["klayout"]
            result["drc_klayout_violations"] = kl.get("violations", 0)
            result["drc_klayout_status"] = "PASS" if kl.get("violations", 0) == 0 else "FAIL"
        return result

    def parse_drc_report(self, drc_log_path: str, drc_tool: str = "magic") -> dict:
        drc_path = Path(drc_log_path)
        if not drc_path.exists():
            status_key = f"drc_{drc_tool}_status"
            return {
                status_key: "REPORT_MISSING",
                "drc_status": "NOT_RUN",
                "drc_total_violations": None,
                "drc_is_clean": False,
                "drc_report_error": "DRC report missing or unreadable — run status is UNKNOWN, not clean",
            }
        try:
            text = drc_path.read_text()
        except OSError:
            status_key = f"drc_{drc_tool}_status"
            return {
                status_key: "ERROR",
                "drc_status": "NOT_RUN",
                "drc_total_violations": None,
                "drc_is_clean": False,
                "drc_report_error": "DRC report missing or unreadable — run status is UNKNOWN, not clean",
            }
        total = 0
        by_rule = {}
        locations = []
        for line in text.splitlines():
            if line.startswith("DRC_TOTAL:"):
                try:
                    total = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith("VIOLATION:"):
                parts = line[len("VIOLATION:"):].strip().split()
                if len(parts) >= 2:
                    rule = parts[0]
                    layer = parts[1]
                    by_rule[rule] = by_rule.get(rule, 0) + 1
                    coords = {}
                    if len(parts) > 2:
                        coord_text = " ".join(parts[2:])
                        cm = re.search(r'\(([-\d.]+)\s+([-\d.]+)\)\s*\(([-\d.]+)\s+([-\d.]+)\)', coord_text)
                        if cm:
                            coords = {"x1": float(cm.group(1)), "y1": float(cm.group(2)),
                                      "x2": float(cm.group(3)), "y2": float(cm.group(4))}
                    locations.append({"rule": rule, "layer": layer, **coords})
        status = "PASS" if total == 0 else "FAIL"
        status_key = f"drc_{drc_tool}_status"
        return {
            status_key: status,
            "drc_status": status,
            "drc_total_violations": total,
            "drc_by_category": by_rule,
            "drc_locations": locations,
            "drc_is_clean": total == 0,
        }

    def parse_lvs_report(self, lvs_comp_path: str) -> dict:
        lvs_path = Path(lvs_comp_path)
        if not lvs_path.exists():
            return {"lvs_result": "ERROR", "lvs_status": "NOT_RUN",
                    "lvs_unmatched_devices": None, "lvs_unmatched_nets": None,
                    "lvs_short_count": None, "lvs_open_count": None,
                    "lvs_parameter_mismatches": None, "lvs_is_clean": False}
        try:
            text = lvs_path.read_text()
        except OSError:
            return {"lvs_result": "ERROR", "lvs_status": "ERROR",
                    "lvs_unmatched_devices": None, "lvs_unmatched_nets": None,
                    "lvs_short_count": None, "lvs_open_count": None,
                    "lvs_parameter_mismatches": None, "lvs_is_clean": False}
        result = "FAIL"
        unmatched_devices = 0
        unmatched_nets = 0
        param_mismatches = 0
        short_count = 0
        open_count = 0
        for line in text.splitlines():
            if "Circuits match uniquely" in line:
                result = "CLEAN"
            m = re.search(r"Unmatched Devices:\s+(\d+)", line)
            if m:
                unmatched_devices = int(m.group(1))
            m = re.search(r"Unmatched Nets:\s+(\d+)", line)
            if m:
                unmatched_nets = int(m.group(1))
            m = re.search(r"Parameter mismatches:\s+(\d+)", line)
            if m:
                param_mismatches = int(m.group(1))
            m = re.search(r"Shorts:\s+(\d+)", line)
            if m:
                short_count = int(m.group(1))
            m = re.search(r"Opens?\s*:\s*(\d+)", line)
            if m:
                open_count = int(m.group(1))
        is_clean = (
            result == "CLEAN" and
            unmatched_devices == 0 and
            unmatched_nets == 0 and
            param_mismatches == 0 and
            short_count == 0 and
            open_count == 0
        )
        lvs_status = "PASS" if is_clean else "FAIL"
        return {
            "lvs_result": result,
            "lvs_status": lvs_status,
            "lvs_unmatched_devices": unmatched_devices,
            "lvs_unmatched_nets": unmatched_nets,
            "lvs_parameter_mismatches": param_mismatches,
            "lvs_short_count": short_count,
            "lvs_open_count": open_count,
            "lvs_is_clean": is_clean,
        }

    def parse_power_report(self, power_report_path: str) -> dict:
        power_path = Path(power_report_path)
        if not power_path.exists():
            return {"power_status": "NOT_RUN", "total_power_mw": None, "leakage_mw": None,
                    "internal_mw": None, "switching_mw": None,
                    "max_ir_drop_mv": None, "mean_ir_drop_mv": None, "ir_violation_count": None}
        try:
            text = power_path.read_text()
        except OSError:
            return {"power_status": "ERROR", "total_power_mw": None, "leakage_mw": None,
                    "internal_mw": None, "switching_mw": None,
                    "max_ir_drop_mv": None, "mean_ir_drop_mv": None, "ir_violation_count": None}
        total = 0.0
        leakage = 0.0
        internal = 0.0
        switching = 0.0
        parsed_ok = False
        for line in text.splitlines():
            m = re.search(r"Total\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", line)
            if m:
                internal = float(m.group(1))
                switching = float(m.group(2))
                leakage = float(m.group(3))
                total = float(m.group(4))
                parsed_ok = True
        if not parsed_ok:
            for line in text.splitlines():
                m = re.search(r"Total\s+Power[:\s]+([\d.eE+-]+)\s*m?W", line, re.IGNORECASE)
                if m:
                    total = float(m.group(1))
                    parsed_ok = True
        if not parsed_ok:
            lines = text.splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and parts[0].lower() == "total":
                    try:
                        vals = [float(p) for p in parts[1:5]]
                        internal, switching, leakage, total = vals
                        parsed_ok = True
                    except (ValueError, IndexError):
                        pass
        status = "DONE" if parsed_ok else "ERROR"
        return {
            "power_status": status, "total_power_mw": total, "leakage_mw": leakage,
            "internal_mw": internal, "switching_mw": switching,
            "max_ir_drop_mv": None, "mean_ir_drop_mv": None, "ir_violation_count": None,
        }

    def parse_em_report(self, em_report_path: str) -> dict:
        em_path = Path(em_report_path)
        if not em_path.exists():
            return {"em_status": "NOT_RUN", "em_total_violations": None,
                    "em_max_current_density_ma_um": None, "em_is_clean": False}
        try:
            text = em_path.read_text()
        except OSError:
            return {"em_status": "ERROR", "em_total_violations": None,
                    "em_max_current_density_ma_um": None, "em_is_clean": False}
        violations = 0
        max_cd = 0.0
        for line in text.splitlines():
            if "EM Violation" in line or "EM violation" in line:
                violations += 1
                m = re.search(r"([\d.]+)\s*\(limit\s+([\d.]+)\)", line)
                if m:
                    max_cd = max(max_cd, float(m.group(1)))
            m = re.search(r"Max\s+current\s+density\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                max_cd = max(max_cd, float(m.group(1)))
        is_clean = violations == 0
        return {
            "em_status": "PASS" if is_clean else "FAIL",
            "em_total_violations": violations,
            "em_max_current_density_ma_um": max_cd,
            "em_is_clean": is_clean,
        }

    def parse_decap_report(self, decap_log_path: str) -> dict:
        decap_path = Path(decap_log_path)
        if not decap_path.exists():
            return {"decap_status": "NOT_RUN", "decap_total_cells": None,
                    "decap_capacitance_pf": None, "decap_coverage_pct": None}
        try:
            text = decap_path.read_text()
        except OSError:
            return {"decap_status": "ERROR", "decap_total_cells": None,
                    "decap_capacitance_pf": None, "decap_coverage_pct": None}
        total = 0
        cap = 0.0
        for line in text.splitlines():
            m = re.search(r"Inserted\s+(\d+)\s+decap\s+cells", line, re.IGNORECASE)
            if m:
                total = int(m.group(1))
            m = re.search(r"Decap\s+capacitance\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                cap = float(m.group(1))
        return {
            "decap_status": "DONE",
            "decap_total_cells": total,
            "decap_capacitance_pf": cap,
            "decap_coverage_pct": None,
            "decap_coverage_note": "not_measured",
        }

    def parse_scan_report(self, scan_log_path: str) -> dict:
        scan_path = Path(scan_log_path)
        if not scan_path.exists():
            return {"scan_status": "NOT_RUN", "scan_total_flops": None,
                    "scan_scanned_flops": None, "scan_coverage_pct": None}
        try:
            text = scan_path.read_text()
        except OSError:
            return {"scan_status": "ERROR", "scan_total_flops": None,
                    "scan_scanned_flops": None, "scan_coverage_pct": None}
        total = 0
        scanned = 0
        for line in text.splitlines():
            m = re.search(r"Total\s+flip.flops\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                total = int(m.group(1))
            m = re.search(r"Scanned\s+flip.flops\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                scanned = int(m.group(1))
        coverage = (scanned / total * 100.0) if total else 0.0
        return {
            "scan_status": "DONE",
            "scan_total_flops": total,
            "scan_scanned_flops": scanned,
            "scan_coverage_pct": coverage,
        }

    def parse_atpg_report(self, atpg_report_path: str) -> dict:
        atpg_path = Path(atpg_report_path)
        if not atpg_path.exists():
            return {"atpg_status": "NOT_RUN", "atpg_total_patterns": None,
                    "atpg_fault_coverage_pct": None, "atpg_detected_faults": None}
        try:
            text = atpg_path.read_text()
        except OSError:
            return {"atpg_status": "ERROR", "atpg_total_patterns": None,
                    "atpg_fault_coverage_pct": None, "atpg_detected_faults": None}
        total_patterns = 0
        detected = 0
        total_faults = 0
        for line in text.splitlines():
            m = re.search(r"Total\s+patterns\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                total_patterns = int(m.group(1))
            m = re.search(r"Detected\s+faults\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                detected = int(m.group(1))
            m = re.search(r"Total\s+faults\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                total_faults = int(m.group(1))
        coverage = (detected / total_faults * 100.0) if total_faults else 0.0
        return {
            "atpg_status": "DONE",
            "atpg_total_patterns": total_patterns,
            "atpg_detected_faults": detected,
            "atpg_total_faults": total_faults,
            "atpg_fault_coverage_pct": coverage,
        }

    def parse_formal_report(self, formal_log_path: str) -> dict:
        formal_path = Path(formal_log_path)
        if not formal_path.exists():
            return {"formal_status": "NOT_RUN", "formal_compare_points": None,
                    "formal_is_equivalent": False, "formal_failures": None}
        try:
            text = formal_path.read_text()
        except OSError:
            return {"formal_status": "ERROR", "formal_compare_points": None,
                    "formal_is_equivalent": False, "formal_failures": None}
        points = 0
        is_equiv = True
        for line in text.splitlines():
            m = re.search(r"Compare\s+points\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                points = int(m.group(1))
            if "not equivalent" in line.lower():
                is_equiv = False
        return {"formal_status": "PASS" if is_equiv else "FAIL",
                "formal_compare_points": points, "formal_is_equivalent": is_equiv,
                "formal_failures": 0 if is_equiv else points}

    def parse_antenna_report(self, antenna_report_path: str) -> dict:
        ant_path = Path(antenna_report_path)
        if not ant_path.exists():
            return {"antenna_total_violations": None, "antenna_max_ratio": None,
                    "antenna_is_clean": False, "antenna_status": "NOT_RUN"}
        try:
            text = ant_path.read_text()
        except OSError:
            return {"antenna_total_violations": None, "antenna_max_ratio": None,
                    "antenna_is_clean": False, "antenna_status": "ERROR"}
        violations = 0
        max_ratio = 0.0
        for line in text.splitlines():
            m = re.search(r"Antenna\s+violation\s+on\s+net\s+(\S+)\s+ratio\s+([\d.]+)", line, re.IGNORECASE)
            if m:
                violations += 1
                max_ratio = max(max_ratio, float(m.group(2)))
            m = re.search(r"Total\s+violations\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                violations = max(violations, int(m.group(1)))
        is_clean = violations == 0
        return {"antenna_total_violations": violations, "antenna_max_ratio": max_ratio,
                "antenna_is_clean": is_clean, "antenna_status": "PASS" if is_clean else "FAIL"}

    def parse_density_report(self, density_report_path: str) -> dict:
        den_path = Path(density_report_path)
        if not den_path.exists():
            return {"density_pct": None, "density_min_pct": None, "density_max_pct": None,
                    "density_violations": None, "density_status": "NOT_RUN"}
        try:
            text = den_path.read_text()
        except OSError:
            return {"density_pct": None, "density_min_pct": None, "density_max_pct": None,
                    "density_violations": None, "density_status": "ERROR"}
        density = 0.0
        min_d = 0.0
        max_d = 0.0
        violations = 0
        for line in text.splitlines():
            m = re.search(r"^Density\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                density = float(m.group(1))
            m = re.search(r"Min\s+density\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                min_d = float(m.group(1))
            m = re.search(r"Max\s+density\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                max_d = float(m.group(1))
            m = re.search(r"Violations\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                violations = int(m.group(1))
        return {"density_pct": density, "density_min_pct": min_d, "density_max_pct": max_d,
                "density_violations": violations,
                "density_status": "PASS" if violations == 0 else "FAIL"}

    def parse_signoff_report(self, setup_rpt_path: str) -> dict:
        setup_path = Path(setup_rpt_path)
        if not setup_path.exists():
            return {
                "signoff_timing_status": "ERROR",
                "signoff_setup_wns_ns": None,
                "signoff_setup_tns_ns": None,
                "signoff_hold_whs_ns": None,
                "signoff_hold_ths_ns": None,
                "signoff_setup_satisfied": False,
                "signoff_hold_satisfied": False,
                "signoff_report_error": "STA report missing or unreadable — signoff timing status is ERROR, not clean",
            }
        try:
            text = setup_path.read_text()
        except OSError:
            return {
                "signoff_timing_status": "ERROR",
                "signoff_setup_wns_ns": None,
                "signoff_setup_tns_ns": None,
                "signoff_hold_whs_ns": None,
                "signoff_hold_ths_ns": None,
                "signoff_setup_satisfied": None,
                "signoff_hold_satisfied": None,
                "signoff_report_error": "STA report missing or unreadable — signoff timing status is ERROR, not clean",
            }
        endpoints = 0
        setup_wns = 0.0
        setup_tns = 0.0
        for line in text.splitlines():
            m = re.search(r"wns\s+(-?[\d.]+)", line, re.IGNORECASE)
            if m:
                setup_wns = float(m.group(1))
            m = re.search(r"tns\s+(-?[\d.]+)", line, re.IGNORECASE)
            if m:
                setup_tns = float(m.group(1))
            m = re.search(r"Endpoints\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                endpoints = int(m.group(1))
        return {"signoff_timing_status": "PASS" if setup_wns >= 0 else "FAIL",
                "signoff_setup_wns_ns": setup_wns, "signoff_setup_tns_ns": setup_tns,
                "signoff_hold_whs_ns": None, "signoff_hold_ths_ns": None,
                "signoff_setup_satisfied": setup_wns is not None and setup_wns >= 0,
                "signoff_hold_satisfied": None}

    def parse_clock_gating_report(self, cg_log_path: str) -> dict:
        cg_path = Path(cg_log_path)
        if not cg_path.exists():
            return {"cg_status": "NOT_RUN", "cg_total_registers": None,
                    "cg_gated_registers": None, "cg_power_savings_pct": None}
        try:
            text = cg_path.read_text()
        except OSError:
            return {"cg_status": "ERROR", "cg_total_registers": None,
                    "cg_gated_registers": None, "cg_power_savings_pct": None}
        total = 0
        gated = 0
        for line in text.splitlines():
            m = re.search(r"Total\s+registers\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                total = int(m.group(1))
            m = re.search(r"Gated\s+registers\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                gated = int(m.group(1))
        savings = (gated / total * 100.0) if total else 0.0
        return {"cg_status": "DONE", "cg_total_registers": total, "cg_gated_registers": gated, "cg_power_savings_pct": savings}

    def parse_pro_report(self, pro_log_path: str) -> dict:
        pro_path = Path(pro_log_path)
        if not pro_path.exists():
            return {"pro_status": "NOT_RUN", "pro_buffer_count": None,
                    "pro_slack_improvement_ns": None, "pro_setup_fixed": None, "pro_hold_fixed": None}
        try:
            text = pro_path.read_text()
        except OSError:
            return {"pro_status": "ERROR", "pro_buffer_count": None,
                    "pro_slack_improvement_ns": None, "pro_setup_fixed": None, "pro_hold_fixed": None}
        buffers = 0
        slack_imp = 0.0
        setup_fixed = 0
        hold_fixed = 0
        for line in text.splitlines():
            m = re.search(r"Inserted\s+(\d+)\s+buffer", line, re.IGNORECASE)
            if m:
                buffers = int(m.group(1))
            m = re.search(r"Slack\s+improvement\s*:\s*([-\d.]+)", line, re.IGNORECASE)
            if m:
                slack_imp = float(m.group(1))
            m = re.search(r"Setup\s+violations\s+fixed\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                setup_fixed = int(m.group(1))
            m = re.search(r"Hold\s+violations\s+fixed\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                hold_fixed = int(m.group(1))
        return {"pro_status": "DONE", "pro_buffer_count": buffers, "pro_slack_improvement_ns": slack_imp,
                "pro_setup_fixed": setup_fixed, "pro_hold_fixed": hold_fixed}

    def parse_si_report(self, si_report_path: str) -> dict:
        si_path = Path(si_report_path)
        if not si_path.exists():
            return {"si_status": "NOT_RUN", "si_crosstalk_violations": None,
                    "si_max_delta_delay_ns": None, "si_is_clean": False}
        try:
            text = si_path.read_text()
        except OSError:
            return {"si_status": "ERROR", "si_crosstalk_violations": None,
                    "si_max_delta_delay_ns": None, "si_is_clean": False}
        violations = 0
        max_delay = 0.0
        for line in text.splitlines():
            m = re.search(r"Crosstalk\s+violations?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                violations = int(m.group(1))
            m = re.search(r"Max\s+delta\s+delay\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                max_delay = max(max_delay, float(m.group(1)))
            m = re.search(r"Crosstalk\s+violation\s+on\s+(\S+)\s+delta\s+([\d.]+)", line, re.IGNORECASE)
            if m:
                violations += 1
                max_delay = max(max_delay, float(m.group(2)))
        is_clean = violations == 0
        return {"si_status": "PASS" if is_clean else "FAIL",
                "si_crosstalk_violations": violations, "si_max_delta_delay_ns": max_delay,
                "si_is_clean": is_clean}

    def parse_hierarchical_partition_report(self, partition_log_path: str) -> dict:
        metrics: dict = {
            "hp_total_blocks": 0,
            "hp_runtime_sec": 0.0,
        }
        log_path = Path(partition_log_path)
        if not log_path.exists():
            return metrics
        text = log_path.read_text()
        for line in text.splitlines():
            m = re.search(r"Partition:\s+(\S+)\s+instances\s+(\d+)", line, re.IGNORECASE)
            if m:
                metrics["hp_total_blocks"] = metrics.get("hp_total_blocks", 0) + 1
        return metrics

    def parse_block_synthesis_report(self, block_synth_log_path: str) -> dict:
        metrics: dict = {
            "bs_total_blocks": 0,
            "bs_total_cells": 0,
            "bs_total_area_um2": 0.0,
            "bs_estimated_power_mw": 0.0,
        }
        log_path = Path(block_synth_log_path)
        if not log_path.exists():
            return metrics
        text = log_path.read_text()
        for line in text.splitlines():
            m = re.search(r"Number\s+of\s+blocks?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                metrics["bs_total_blocks"] = int(m.group(1))
            m = re.search(r"Number\s+of\s+cells\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                metrics["bs_total_cells"] = int(m.group(1))
            m = re.search(r"Chip\s+area\s+for\s+top\s+module\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                metrics["bs_total_area_um2"] = float(m.group(1))
        return metrics

    def parse_top_floorplan_report(self, top_fp_log_path: str) -> dict:
        metrics: dict = {
            "tf_total_blocks": 0,
            "tf_die_width_um": 0.0,
            "tf_die_height_um": 0.0,
        }
        log_path = Path(top_fp_log_path)
        if not log_path.exists():
            return metrics
        text = log_path.read_text()
        for line in text.splitlines():
            m = re.search(r"Die\s+area\s*:\s*([\d.]+)\s*x\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                metrics["tf_die_width_um"] = float(m.group(1))
                metrics["tf_die_height_um"] = float(m.group(2))
            m = re.search(r"Block\s+(\S+)\s+placed", line, re.IGNORECASE)
            if m:
                metrics["tf_total_blocks"] = metrics.get("tf_total_blocks", 0) + 1
        return metrics

    def parse_d2d_interface_report(self, d2d_report_path: str) -> dict:
        metrics: dict = {
            "d2d_cross_boundary_paths": 0,
            "d2d_total_violations": 0,
            "d2d_max_cross_delay_ns": 0.0,
            "d2d_is_clean": True,
        }
        report_path = Path(d2d_report_path)
        if not report_path.exists():
            return metrics
        text = report_path.read_text()
        violations = 0
        for line in text.splitlines():
            m = re.search(r"Cross-boundary\s+paths?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                metrics["d2d_cross_boundary_paths"] = int(m.group(1))
            m = re.search(r"Interface\s+violations?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                violations = int(m.group(1))
            m = re.search(r"Interface\s+violation\s+on\s+(\S+)\s+delay\s+([\d.]+)", line, re.IGNORECASE)
            if m:
                metrics["d2d_max_cross_delay_ns"] = max(
                    metrics["d2d_max_cross_delay_ns"], float(m.group(2))
                )
        metrics["d2d_total_violations"] = violations
        metrics["d2d_is_clean"] = violations == 0
        return metrics

    def parse_yield_report(self, yield_report_path: str) -> dict:
        yield_path = Path(yield_report_path)
        if not yield_path.exists():
            return {"yield_status": "NOT_RUN", "yield_redundant_vias": None,
                    "yield_repair_coverage_pct": None, "yield_critical_spots": None}
        try:
            text = yield_path.read_text()
        except OSError:
            return {"yield_status": "ERROR", "yield_redundant_vias": None,
                    "yield_repair_coverage_pct": None, "yield_critical_spots": None}
        vias = 0
        coverage = 0.0
        critical = 0
        for line in text.splitlines():
            m = re.search(r"Redundant\s+vias?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                vias = int(m.group(1))
            m = re.search(r"Repair\s+coverage\s*:\s*([\d.]+)", line, re.IGNORECASE)
            if m:
                coverage = float(m.group(1))
            m = re.search(r"Critical\s+spots?\s*:\s*(\d+)", line, re.IGNORECASE)
            if m:
                critical = int(m.group(1))
        return {"yield_status": "DONE", "yield_redundant_vias": vias, "yield_repair_coverage_pct": coverage, "yield_critical_spots": critical}

    def parse_all(self):
        metrics = {}
        metrics["timing_unit"] = "ns"
        metrics.update(self.parse_timing())
        metrics.update(self.parse_utilization())
        metrics.update(self.parse_runtime())

        # DRC: try combined JSON first, fall back to raw text reports
        drc_combined = self.reports_dir / "drc_combined.json"
        if drc_combined.exists():
            metrics.update(self.parse_drc_combined_json(drc_combined))
        else:
            drc_path = self.reports_dir / "drc_raw.txt"
            metrics.update(self.parse_drc_report(str(drc_path), "magic"))
            klayout_drc_path = self.reports_dir / "klayout_drc.xml"
            if not klayout_drc_path.exists():
                klayout_drc_path = self.reports_dir / "drc_klayout.xml"
            if klayout_drc_path.exists():
                metrics.update(self.parse_drc_report(str(klayout_drc_path), "klayout"))

        # LVS: try lvs_report.txt first, fall back to lvs_comp.out
        lvs_path = self.reports_dir / "lvs_report.txt"
        if not lvs_path.exists():
            lvs_path = self.reports_dir / "lvs_comp.out"
        metrics.update(self.parse_lvs_report(str(lvs_path)))
        power_path = self.reports_dir / "power_report.txt"
        metrics.update(self.parse_power_report(str(power_path)))
        em_path = self.reports_dir / "em_report.txt"
        metrics.update(self.parse_em_report(str(em_path)))
        decap_path = self.reports_dir / "decap_log.txt"
        metrics.update(self.parse_decap_report(str(decap_path)))
        scan_path = self.reports_dir / "scan_log.txt"
        metrics.update(self.parse_scan_report(str(scan_path)))
        atpg_path = self.reports_dir / "atpg_report.txt"
        metrics.update(self.parse_atpg_report(str(atpg_path)))
        formal_path = self.reports_dir / "formal_log.txt"
        metrics.update(self.parse_formal_report(str(formal_path)))
        antenna_path = self.reports_dir / "antenna_report.txt"
        metrics.update(self.parse_antenna_report(str(antenna_path)))
        density_path = self.reports_dir / "density_report.txt"
        metrics.update(self.parse_density_report(str(density_path)))
        # Signoff: look in run_dir root for corner reports, then reports dir
        if self.run_dir:
            for corner in ("worst", "typical", "best"):
                signoff_path = self.run_dir / f"signoff_{corner}_setup.rpt"
                if signoff_path.exists():
                    metrics.update(self.parse_signoff_report(str(signoff_path)))
                    break
        else:
            signoff_path = self.reports_dir / "signoff_setup.rpt"
            if signoff_path.exists():
                metrics.update(self.parse_signoff_report(str(signoff_path)))
        cg_path = self.reports_dir / "clock_gating_log.txt"
        metrics.update(self.parse_clock_gating_report(str(cg_path)))
        pro_path = self.reports_dir / "pro_log.txt"
        metrics.update(self.parse_pro_report(str(pro_path)))
        si_path = self.reports_dir / "si_report.txt"
        metrics.update(self.parse_si_report(str(si_path)))
        yield_path = self.reports_dir / "yield_report.txt"
        metrics.update(self.parse_yield_report(str(yield_path)))
        partition_path = self.reports_dir / "partition_log.txt"
        metrics.update(self.parse_hierarchical_partition_report(str(partition_path)))
        block_synth_path = self.reports_dir / "block_synth_log.txt"
        metrics.update(self.parse_block_synthesis_report(str(block_synth_path)))
        top_fp_path = self.reports_dir / "top_floorplan_log.txt"
        metrics.update(self.parse_top_floorplan_report(str(top_fp_path)))
        d2d_path = self.reports_dir / "d2d_report.txt"
        metrics.update(self.parse_d2d_interface_report(str(d2d_path)))
        gds_path = self.reports_dir / "results" / "6_final.gds"
        if gds_path.exists():
            st = gds_path.stat()
            metrics["gds_mtime"] = st.st_mtime
            metrics["gds_size_bytes"] = st.st_size
        return metrics
