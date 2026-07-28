from intelligence.prediction_outcome_record import PredictionOutcomeRecord
from intelligence.outcome_comparator import OutcomeComparator
from intelligence.calibration_metrics import CalibrationEngine
from intelligence.validation_engine import ValidationEngine

def run_verification():
    print("Verification: Prediction Validation & Calibration Engine")
    
    # Mock data
    record = PredictionOutcomeRecord("run_001", {"timing": 0.8}, {"timing": 0.4})
    
    # Test Comparator
    comparator = OutcomeComparator()
    error = comparator.compare(record)
    assert error["timing_error"] == 0.4
    print("Comparator: PASS")
    
    # Test Calibration
    cal = CalibrationEngine()
    err = cal.calculate_calibration_error([0.8], [0.4])
    assert err == 0.4
    print("Calibration: PASS")
    
    # Test Validation
    val = ValidationEngine()
    assert val.validate_confidence([], []) > 0
    print("Validation: PASS")

if __name__ == "__main__":
    run_verification()
