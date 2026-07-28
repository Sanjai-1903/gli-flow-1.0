import json
import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone


@dataclass
class FailureEvolutionTracker:
    """Tracks failure evolution over time using historical Failure Atlas data."""

    db_path: Optional[str] = None

    def __post_init__(self):
        self._history_path = str(Path.home() / ".gli_flow" / "failure_evolution.json")

    def track_failure(self, failure_fingerprint: str):
        record = {
            "fingerprint": failure_fingerprint,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "detected",
        }
        history = []
        if os.path.exists(self._history_path):
            with open(self._history_path) as f:
                history = json.load(f)
        history.append(record)
        if len(history) > 10000:
            history = history[-10000:]
        os.makedirs(os.path.dirname(self._history_path), exist_ok=True)
        with open(self._history_path, "w") as f:
            json.dump(history, f, indent=2)

    def get_evolution_summary(self, failure_fingerprint: str) -> Dict[str, Any]:
        if not os.path.exists(self._history_path):
            return {"occurrences": 0, "first_seen": None, "last_seen": None}
        with open(self._history_path) as f:
            history = json.load(f)
        relevant = [h for h in history if h.get("fingerprint") == failure_fingerprint]
        if not relevant:
            return {"occurrences": 0, "first_seen": None, "last_seen": None}
        return {
            "occurrences": len(relevant),
            "first_seen": relevant[0]["timestamp"],
            "last_seen": relevant[-1]["timestamp"],
        }
