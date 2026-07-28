"""
CDC (Clock Domain Crossing) detection.
GLI-FLOW v1.0 does NOT perform CDC analysis.
This module detects multi-clock designs and displays mandatory disclaimers.
"""

import logging
import re
from pathlib import Path
from typing import List

log = logging.getLogger(__name__)


def count_clock_domains(rtl_files: List[str], sdc_file: str = None) -> dict:
    """Count clock domains in design.

    Primary source of truth is SDC create_clock definitions.
    RTL-level clock signal detection is supplementary for warning purposes only.
    """
    sdc_clocks = set()
    rtl_clock_signals = set()

    if sdc_file and Path(sdc_file).exists():
        try:
            sdc_content = Path(sdc_file).read_text()
            clock_matches = re.findall(
                r"create_clock[^\n]+\[get_ports\s+([^\]]+)\]", sdc_content
            )
            sdc_clocks.update(clock_matches)

            gen_clocks = re.findall(
                r"create_generated_clock[^\n]+-name\s+(\S+)", sdc_content
            )
            sdc_clocks.update(gen_clocks)

            wave_clocks = re.findall(
                r"create_clock[^\n]+-name\s+(\S+)", sdc_content
            )
            sdc_clocks.update(wave_clocks)
        except Exception as e:
            log.warning(f"Failed to parse SDC file {sdc_file}: {e}")

    for rtl_file in rtl_files:
        try:
            content = Path(rtl_file).read_text(errors='ignore')
            edges = re.findall(r"(?:posedge|negedge)\s+(\w+)", content)
            for sig in edges:
                if any(kw in sig.lower() for kw in ['clk', 'clock', 'clk_', '_clk', 'ck', 'osc']):
                    rtl_clock_signals.add(sig)
        except Exception as e:
            log.warning(f"Failed to parse RTL file {rtl_file}: {e}")

    clock_count = len(sdc_clocks) if sdc_clocks else len(rtl_clock_signals)
    clock_names = list(sdc_clocks) if sdc_clocks else list(rtl_clock_signals)
    multi_clock = clock_count > 1

    return {
        "clock_count": clock_count,
        "clock_names": clock_names,
        "multi_clock": multi_clock,
        "rtl_clock_signals": list(rtl_clock_signals),
        "sdc_clock_count": len(sdc_clocks),
    }


CDC_DISCLAIMER = """
┌─────────────────────────────────────────────────────┐
│ ⚠  CDC ANALYSIS NOT PERFORMED                      │
│                                                     │
│ {n} clock domain(s) detected in this design.        │
│                                                     │
│ GLI-FLOW v1.0 does NOT perform clock domain         │
│ crossing (CDC) analysis. CDC violations are a       │
│ leading cause of functional failures in silicon.    │
│                                                     │
│ REQUIRED before tapeout:                            │
│   Use a dedicated CDC tool (Synopsys SpyGlass,      │
│   Mentor Questa CDC, or open-source sv-cdc)         │
│   to verify all clock domain crossings.             │
│                                                     │
│ LVS CLEAN and DRC CLEAN do NOT indicate CDC safety. │
└─────────────────────────────────────────────────────┘
"""
