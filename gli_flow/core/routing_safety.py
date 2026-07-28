"""
Routing safety checks for fail-fast behavior.
"""

import re
import csv
import logging
from pathlib import Path
from gli_flow.core.exceptions import RoutingOverflowError

log = logging.getLogger(__name__)

OVERFLOW_THRESHOLD = 0.05


def check_global_routing_overflow(
    log_path: str,
    metrics_path: str = None,
    threshold: float = OVERFLOW_THRESHOLD,
    gds_path: str = None,
) -> dict:
    """Parse global routing output for overflow metrics."""
    overflow_h = 0.0
    overflow_v = 0.0
    overflow_total = 0

    final_gds_ok = gds_path and Path(gds_path).is_file() and Path(gds_path).stat().st_size > 0
    if final_gds_ok:
        log.info("Final GDS exists — routing completed. Skipping overflow log parsing.")
        max_overflow = 0.0
        result = {
            "overflow_h": 0.0,
            "overflow_v": 0.0,
            "overflow_total": 0,
            "max_overflow": max_overflow,
            "exceeds_threshold": False,
        }
        return result

    if metrics_path:
        try:
            with open(metrics_path) as f:
                reader = csv.DictReader(f)
                row = next(reader, None)
            if row:
                overflow_h = float(row.get("globalroute__overflow__h", row.get("overflow_h", 0)) or 0)
                overflow_v = float(row.get("globalroute__overflow__v", row.get("overflow_v", 0)) or 0)
        except Exception as e:
            log.warning(f"Failed to parse metrics CSV {metrics_path}: {e}")

    if overflow_h == 0 and overflow_v == 0:
        try:
            content = Path(log_path).read_text(errors='ignore')

            patterns = [
                (r"Horizontal overflow:\s*([\d.]+)%", "h"),
                (r"Vertical overflow:\s*([\d.]+)%", "v"),
                (r"GRT-0042.*overflow\s+([\d.]+)", "total"),
                (r"Detailed Routing.*overflow\s+([\d.]+)", "total"),
            ]

            for pattern, direction in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    val = float(match.group(1))
                    if val > 1:
                        val = val / 100
                    if direction == "h":
                        overflow_h = val
                    elif direction == "v":
                        overflow_v = val
                    else:
                        overflow_total = val

        except Exception as e:
            log.warning(f"Could not parse routing overflow: {e}")

    max_overflow = max(overflow_h, overflow_v, overflow_total)

    result = {
        "overflow_h": overflow_h,
        "overflow_v": overflow_v,
        "overflow_total": overflow_total,
        "max_overflow": max_overflow,
        "exceeds_threshold": max_overflow > threshold,
    }

    if max_overflow > threshold:
        raise RoutingOverflowError(max_overflow)

    if max_overflow > 0:
        log.warning(
            f"Routing overflow {max_overflow:.1%} "
            f"(below {threshold:.0%} threshold, proceeding to detail routing)"
        )

    return result
