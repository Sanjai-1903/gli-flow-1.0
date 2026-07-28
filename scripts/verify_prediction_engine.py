from intelligence.prediction_dataset_builder import PredictionDatasetBuilder
from intelligence.failure_risk_engine import FailureRiskEngine
from intelligence.prediction_models import ReadinessPredictor, ConvergencePredictor
from intelligence.prediction_analysis import SimilarityEngine, ConfidenceEngine, ExplainabilityEngine, PredictionQualityEngine
from intelligence.intelligence_records import ExecutionIntelligenceRecord

def run_verification():
    print("Functional Verification: GLI Execution Intelligence Prediction Engine")
    
    # Mock Record
    record = ExecutionIntelligenceRecord("f1", "c1", "r1", 0.9, {"area": 100}, "SUCCESS")
    
    # Test Builder
    builder = PredictionDatasetBuilder()
    data = builder.build(record)
    assert data.target["outcome"] == "SUCCESS"
    print("DatasetBuilder: PASS")
    
    # Test Risk Engine
    risk = FailureRiskEngine().predict_risk(data.features)
    assert "timing" in risk
    print("FailureRiskEngine: PASS")
    
    # Test Predictors
    assert ReadinessPredictor().predict_readiness(data.features) > 0
    assert ConvergencePredictor().predict_convergence(data.features) > 0
    print("Predictors: PASS")
    
    # Test Analysis
    assert SimilarityEngine().find_similar(data.features) == ["run_001", "run_002"]
    assert ConfidenceEngine().measure_confidence(None) == 0.9
    print("Analysis Engines: PASS")

if __name__ == "__main__":
    run_verification()
