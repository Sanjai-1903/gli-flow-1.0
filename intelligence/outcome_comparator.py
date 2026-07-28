from typing import Dict, Any
from intelligence.prediction_outcome_record import PredictionOutcomeRecord

class OutcomeComparator:
    def compare(self, record: PredictionOutcomeRecord) -> Dict[str, float]:
        # Compare predicted risks vs actual outcomes
        comparison = {}
        for metric, pred_val in record.prediction.items():
            actual_val = record.actual_outcome.get(metric, 0.0)
            comparison[f"{metric}_error"] = abs(pred_val - float(actual_val))
        return comparison
