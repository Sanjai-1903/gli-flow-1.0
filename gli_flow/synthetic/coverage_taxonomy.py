TAXONOMY = {
    "Failure Type": [
        "Timing", "Routing", "CTS", "DRC", "LVS", "Power",
        "IR Drop", "Antenna", "Extraction", "Tool Failures",
    ],
    "Root Cause": [
        "Placement", "CTS", "Routing", "Signoff", "Constraints",
        "Tool Config", "PDK", "Extraction", "Floorplan",
        "Clock Skew", "IR Drop", "Cell Density", "Macro Congestion",
    ],
    "Flow Stage": [
        "placement", "cts", "routing", "signoff", "lvs", "extraction",
    ],
    "PDK": ["sky130A"],
    "Design": [
        "counter", "gcd", "uart", "gpio", "fir", "picorv32",
        "ibex", "serv", "opentitan_ibex", "tinyml_accel",
        "sram_controller", "aes_cipher",
    ],
    "Resolution": [
        "Timing Fix", "Routing Fix", "LVS Fix", "IR Drop Fix",
        "DRC Fix", "CTS Fix", "Tool Config Fix", "Extraction Fix",
        "Power Grid Fix", "Floorplan Fix",
    ],
    "QoR Scenario": ["Area", "Power", "Timing", "Density", "Congestion"],
    "Graph Feature": ["fanout", "logic_depth", "resource", "timing_path"],
    "Injection Type": [
        "CLOCK_PERIOD_SWEEP", "UTILIZATION_SWEEP", "FLOORPLAN_SHRINK",
        "MACRO_CONGESTION", "PDN_STRESS", "ROUTING_CONGESTION",
        "TIMING_CONSTRAINT_ERRORS", "MISSING_CONSTRAINTS",
        "DRC_VIOLATIONS", "LVS_MISMATCHES", "TOOL_CONFIGURATION_ERRORS",
        "SKEW_INJECTION", "UNCERTAINTY_CHANGES", "FALSE_PATH_ERRORS",
        "MULTICYCLE_ERRORS", "DENSITY_STRESS", "MACRO_CLUSTERING",
        "CHANNEL_COLLAPSE", "PDN_STARVATION", "IR_DROP_SCENARIOS",
        "EXCESSIVE_SWITCHING", "EXTRACTION_FAILURES", "MISSING_DEVICES",
        "NET_DISCONNECTS", "CORRUPTED_CONFIGS", "MISSING_FILES",
        "VERSION_MISMATCHES",
    ],
}
