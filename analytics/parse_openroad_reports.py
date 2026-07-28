import os
import re


def parse_openroad_reports(report_dir):

    metrics = {
        "wns": 0.0,
        "tns": 0.0,
        "utilization": 0.0,
        "cell_count": 0
    }

    timing_file = os.path.join(
        report_dir,
        "timing.rpt"
    )

    utilization_file = os.path.join(
        report_dir,
        "utilization.rpt"
    )

    try:

        if os.path.exists(timing_file):

            with open(timing_file, "r") as f:
                content = f.read()

            wns_match = re.search(
                r"WNS:\s*(-?\d+\.?\d*)",
                content
            )

            tns_match = re.search(
                r"TNS:\s*(-?\d+\.?\d*)",
                content
            )

            if wns_match:
                metrics["wns"] = float(
                    wns_match.group(1)
                )

            if tns_match:
                metrics["tns"] = float(
                    tns_match.group(1)
                )

    except Exception:
        pass

    try:

        if os.path.exists(utilization_file):

            with open(utilization_file, "r") as f:
                content = f.read()

            util_match = re.search(
                r"Utilization:\s*(\d+\.?\d*)",
                content
            )

            cell_match = re.search(
                r"Total Cells:\s*(\d+)",
                content
            )

            if util_match:
                metrics["utilization"] = float(
                    util_match.group(1)
                )

            if cell_match:
                metrics["cell_count"] = int(
                    cell_match.group(1)
                )

    except Exception:
        pass

    return metrics
