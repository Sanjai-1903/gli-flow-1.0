from gli_flow.regression.detector import detect_regression as _canonical_detect

__all__ = ["detect_regression"]


def detect_regression(current_metrics, baseline_metrics=None,
                      qor_drop_threshold=None, wns_degrade_threshold=None,
                      tns_degrade_threshold=None, utilization_increase_threshold=None):
    kwargs = {}
    if qor_drop_threshold is not None:
        kwargs["qor_drop_threshold"] = qor_drop_threshold
    if wns_degrade_threshold is not None:
        kwargs["wns_degrade_threshold"] = wns_degrade_threshold
    if tns_degrade_threshold is not None:
        kwargs["tns_degrade_threshold"] = tns_degrade_threshold
    if utilization_increase_threshold is not None:
        kwargs["utilization_increase_threshold"] = utilization_increase_threshold
    return _canonical_detect(current_metrics, baseline_metrics, **kwargs)
