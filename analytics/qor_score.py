import sys
sys.path.insert(0, __file__.rsplit("/", 3)[0])

from gli_flow.analytics.qor_score import calculate_qor_score as _canonical_qor


def calculate_qor_score(wns, tns, utilization, runtime, **kwargs):
    result = _canonical_qor(wns=wns, tns=tns, utilization=utilization,
                            runtime=runtime, cell_count=kwargs.get("cell_count", 0))
    return result["score"]
