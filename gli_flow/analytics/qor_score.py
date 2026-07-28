import math

# ──────────────────────────────────────────────
# QoR v2 — Design Quality Score
# ──────────────────────────────────────────────
# Weights (must sum to 1.0)
TIMING_WEIGHT = 0.35
DESIGN_QUALITY_WEIGHT = 0.25
UTILIZATION_WEIGHT = 0.20
DENSITY_WEIGHT = 0.10
RUNTIME_WEIGHT = 0.10

# Timing parameters
TARGET_CLOCK_PERIOD_NS = 10.0

# Density parameters
REF_CELL_COUNT = 25000.0
UTIL_OVERHEAD = 0.30
MAX_UTILIZATION_PCT = 100.0

# Runtime parameters (max 10% influence)
MAX_EXPECTED_RUNTIME_SEC = 3600.0

# Design quality sub-weights
DRC_WEIGHT = 0.40
LVS_WEIGHT = 0.30
SIGNOFF_WEIGHT = 0.30


def _clamp(value, lo, hi):
    if value is None:
        return lo
    return max(lo, min(hi, value))


def _timing_score(wns_ns, tns_ns) -> float:
    if wns_ns is None or tns_ns is None:
        return 0.0
    if wns_ns >= 0:
        tns_ratio = max(0, -tns_ns) / TARGET_CLOCK_PERIOD_NS
        return 1.0 / (1.0 + tns_ratio)
    wns_magnitude = abs(wns_ns)
    return 1.0 / (1.0 + wns_magnitude / TARGET_CLOCK_PERIOD_NS)


def _area_score(utilization) -> float:
    if utilization is None:
        return 0.0
    util_ratio = utilization / MAX_UTILIZATION_PCT
    return _clamp(1.0 - util_ratio ** 2, 0.0, 1.0)


def _density_score(cell_count) -> float:
    if cell_count is None:
        return 0.0
    density_ratio = cell_count / REF_CELL_COUNT
    effective = max(0.0, density_ratio - UTIL_OVERHEAD)
    return _clamp(1.0 - effective ** 2, 0.0, 1.0)


def _runtime_score(runtime_sec) -> float:
    if runtime_sec is None or runtime_sec <= 0:
        return 1.0 if runtime_sec is not None and runtime_sec <= 0 else 0.0
    return _clamp(1.0 - runtime_sec / MAX_EXPECTED_RUNTIME_SEC, 0.0, 1.0)


def _design_quality_score(drc_clean, lvs_clean, signoff_complete) -> float:
    score = 0.0
    if drc_clean is True:
        score += DRC_WEIGHT
    if lvs_clean is True:
        score += LVS_WEIGHT
    if signoff_complete is True:
        score += SIGNOFF_WEIGHT
    return score


def calculate_implementation_score(utilization=None, cell_count=None):
    area_score = _area_score(utilization)
    density_score = _density_score(cell_count)
    score = 0.5 * area_score + 0.5 * density_score
    return round(score, 2)


def calculate_signoff_score(wns=None, tns=None, drc_clean=None, lvs_clean=None, hold_wns=None):
    timing_score = _timing_score(wns, tns)
    penalty = 0.0
    if drc_clean is False:
        penalty += 0.3
    if lvs_clean is False:
        penalty += 0.3
    if hold_wns is not None and hold_wns < 0:
        penalty = 1.0
    score = timing_score * (1.0 - penalty)
    return max(0.0, min(1.0, round(score, 2)))


def calculate_qor_score(
    wns=None, tns=None, utilization=None, runtime=None,
    cell_count=None, hold_wns=None,
    drc_clean=None, lvs_clean=None, signoff_complete=None,
):
    timing_score = _timing_score(wns, tns)
    area_score = _area_score(utilization)
    density_score = _density_score(cell_count)
    runtime_eff = _runtime_score(runtime)
    design_quality = _design_quality_score(drc_clean, lvs_clean, signoff_complete)

    score = (
        TIMING_WEIGHT * timing_score +
        DESIGN_QUALITY_WEIGHT * design_quality +
        UTILIZATION_WEIGHT * area_score +
        DENSITY_WEIGHT * density_score +
        RUNTIME_WEIGHT * runtime_eff
    )

    hold_violation_tapeout_blocking = False
    hold_violation_detail = None
    if hold_wns is not None and hold_wns < 0:
        hold_violation_tapeout_blocking = True
        hold_violation_detail = (
            f"Hold WNS: {hold_wns:.3f}ns — "
            f"Hold violation detected. Timing contribution halved."
        )
        score = (
            TIMING_WEIGHT * timing_score * 0.5 +
            DESIGN_QUALITY_WEIGHT * design_quality +
            UTILIZATION_WEIGHT * area_score +
            DENSITY_WEIGHT * density_score +
            RUNTIME_WEIGHT * runtime_eff
        )

    score = _clamp(score, 0.0, 1.0)

    return {
        "score": round(score, 2),
        "implementation_score": calculate_implementation_score(utilization, cell_count),
        "signoff_score": calculate_signoff_score(wns, tns, drc_clean, lvs_clean, hold_wns),
        "breakdown": {
            "timing": round(timing_score, 2),
            "area": round(area_score, 2),
            "density": round(density_score, 2),
            "design_quality": round(design_quality, 2),
            "runtime_efficiency": round(runtime_eff, 2),
        },
        "weights": {
            "timing": TIMING_WEIGHT,
            "design_quality": DESIGN_QUALITY_WEIGHT,
            "area": UTILIZATION_WEIGHT,
            "density": DENSITY_WEIGHT,
            "runtime": RUNTIME_WEIGHT,
        },
        "hold_violation_tapeout_blocking": hold_violation_tapeout_blocking,
        "hold_violation_detail": hold_violation_detail,
    }
