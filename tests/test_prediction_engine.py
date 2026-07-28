from failure_atlas.prediction.dataset import PredictionDatasetBuilder
from failure_atlas.prediction.risk import FailureRiskEngine
from gli_flow.database.migrations import _get_db_path

def test_prediction():
    db_path = _get_db_path()
    
    # Test Dataset Builder
    builder = PredictionDatasetBuilder(db_path)
    dataset = builder.build()
    print(f"Dataset built with {len(dataset)} records.")
    
    # Test Risk Engine
    engine = FailureRiskEngine(db_path)
    metrics = {"wns": 0.1, "tns": 0.0, "utilization": 0.7, "drc_violations": 5}
    risk = engine.predict_risk(metrics)
    print(f"Risk prediction: {risk}")

if __name__ == "__main__":
    test_prediction()
