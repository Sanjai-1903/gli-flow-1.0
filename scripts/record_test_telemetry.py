from failure_atlas.community_intelligence.telemetry import EscalationTelemetry
import sys

def record_test_events():
    et = EscalationTelemetry()
    et.record(
        event="unknown_failure_detected",
        failure_type="TIMING_VIOLATION",
        tool="OpenROAD",
        details={"slack": -0.05, "run_id": "run_1781605284_5d70499f_picorv32"}
    )
    et.record(
        event="failure_atlas_miss",
        failure_type="UNKNOWN_ERROR",
        tool="Magic",
        details={"error": "Unknown Magic return code", "run_id": "run_1781605284_5d70499f_picorv32"}
    )
    print("Recorded test telemetry events for ATLAS mode.")

if __name__ == "__main__":
    record_test_events()
