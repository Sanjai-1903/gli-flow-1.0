import csv
import os

from pathlib import Path


class TelemetryParser:

    def __init__(self, reports_dir):
        self.reports_dir = Path(reports_dir)

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

        csv_path = self.reports_dir / "metrics.csv"
        if csv_path.exists():
            parsed = self._parse_csv(csv_path)
            if "wns" in parsed:
                metrics["wns"] = parsed["wns"]
            if "tns" in parsed:
                metrics["tns"] = parsed["tns"]

        timing_file = self.reports_dir / "timing.rpt"
        if timing_file.exists():
            lines = self._safe_read_lines(timing_file)
            parsed = self._parse_key_value_lines(lines)
            key_map = {"wns": "wns", "tns": "tns"}
            for k, v in parsed.items():
                if k in key_map:
                    metrics[key_map[k]] = v

        metrics_file = self.reports_dir / "metrics.rpt"
        if metrics_file.exists():
            lines = self._safe_read_lines(metrics_file)
            parsed = self._parse_key_value_lines(lines)
            if "wns" not in metrics and "wns" in parsed:
                metrics["wns"] = parsed["wns"]
            if "tns" not in metrics and "tns" in parsed:
                metrics["tns"] = parsed["tns"]

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

    def parse_all(self):
        metrics = {}
        metrics.update(self.parse_timing())
        metrics.update(self.parse_utilization())
        metrics.update(self.parse_runtime())
        return metrics
