import os
import re


def parse_openroad_reports(report_dir):

    metrics = {

        "wns": 0.0,

        "tns": 0.0,

        "utilization": 0.0,

        "cell_count": 0
    }

    metrics_file = os.path.join(
        report_dir,
        "metrics.rpt"
    )

    if not os.path.exists(metrics_file):

        return metrics

    with open(metrics_file, "r") as f:

        content = f.read()

    wns_match = re.search(
        r"WNS:\s*(-?\d+\.?\d*)",
        content
    )

    tns_match = re.search(
        r"TNS:\s*(-?\d+\.?\d*)",
        content
    )

    util_match = re.search(
        r"Utilization:\s*(\d+\.?\d*)",
        content
    )

    cell_match = re.search(
        r"Total Cells:\s*(\d+)",
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

    if util_match:

        metrics["utilization"] = float(
            util_match.group(1)
        )

    if cell_match:

        metrics["cell_count"] = int(
            cell_match.group(1)
        )

    return metrics
