import os
import re


def parse_openroad_reports(run_dir):

    metrics = {
        "wns": 0.0,
        "tns": 0.0,
        "utilization": 0.0,
        "cell_count": 0
    }

    reports_dir = os.path.join(
        run_dir,
        "reports"
    )

    if not os.path.exists(reports_dir):

        return metrics

    for root, dirs, files in os.walk(reports_dir):

        for file in files:

            path = os.path.join(root, file)

            try:

                with open(path, "r") as f:

                    content = f.read()

                wns_match = re.search(
                    r"WNS[:\s]+(-?\d+\.?\d*)",
                    content
                )

                if wns_match:

                    metrics["wns"] = float(
                        wns_match.group(1)
                    )

                tns_match = re.search(
                    r"TNS[:\s]+(-?\d+\.?\d*)",
                    content
                )

                if tns_match:

                    metrics["tns"] = float(
                        tns_match.group(1)
                    )

                util_match = re.search(
                    r"utilization[:\s]+(\d+\.?\d*)",
                    content,
                    re.IGNORECASE
                )

                if util_match:

                    metrics["utilization"] = float(
                        util_match.group(1)
                    )

                cell_match = re.search(
                    r"cell count[:\s]+(\d+)",
                    content,
                    re.IGNORECASE
                )

                if cell_match:

                    metrics["cell_count"] = int(
                        cell_match.group(1)
                    )

            except (OSError, UnicodeDecodeError, ValueError):
                pass

    return metrics
