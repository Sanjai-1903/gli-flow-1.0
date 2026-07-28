from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from gli_flow.synthetic.dataset_records import TrainingDataset


@dataclass
class QualityReport:
    total_records_processed: int = 0
    deduplication_summary: Dict[str, Any] = field(default_factory=dict)
    label_validation_summary: Dict[str, Any] = field(default_factory=dict)
    consistency_check_summary: Dict[str, Any] = field(default_factory=dict)
    outlier_detection_summary: Dict[str, Any] = field(default_factory=dict)
    overall_status: str = "PENDING"
    issues_found: List[str] = field(default_factory=list)


class QualityEngine:
    def perform_quality_checks(self, dataset: TrainingDataset) -> QualityReport:
        report = QualityReport(
            total_records_processed=len(dataset.failure_records)
            + len(dataset.qor_records)
            + len(dataset.graph_records)
        )

        report.deduplication_summary = self.deduplicate(dataset)
        report.label_validation_summary = self.validate_labels(dataset)
        report.consistency_check_summary = self.check_consistency(dataset)
        report.outlier_detection_summary = self.detect_outliers(dataset)

        if report.issues_found:
            report.overall_status = "ISSUES_FOUND"
        else:
            report.overall_status = "CLEAN"

        return report

    def deduplicate(self, dataset: TrainingDataset) -> Dict[str, Any]:
        fingerprints = set()
        dups = 0
        for record in dataset.failure_records:
            if record.failure_fingerprint in fingerprints:
                dups += 1
            fingerprints.add(record.failure_fingerprint)

        if dataset.resolution_records:
            res_fps = set()
            for r in dataset.resolution_records:
                fp = getattr(r, "failure_fingerprint", None) or getattr(r, "failure_fingerprint_hash", None)
                if fp and fp in res_fps:
                    dups += 1
                if fp:
                    res_fps.add(fp)

        if dups > 0:
            return {"status": "DUPLICATES_FOUND", "count": dups}
        return {"status": "NO_DUPLICATES_FOUND"}

    def validate_labels(self, dataset: TrainingDataset) -> Dict[str, Any]:
        invalid = 0
        for record in dataset.failure_records:
            if not record.root_cause or not record.resolution:
                invalid += 1
        return {"status": "LABELS_VALIDATED", "invalid_count": invalid}

    def check_consistency(self, dataset: TrainingDataset) -> Dict[str, Any]:
        inconsistencies = 0
        for record in dataset.failure_records:
            if record.trust_score < 0 or record.trust_score > 1:
                inconsistencies += 1
        return {"status": "CONSISTENCY_CHECKED", "inconsistencies_found": inconsistencies}

    def detect_outliers(self, dataset: TrainingDataset) -> Dict[str, Any]:
        outliers = 0
        for record in dataset.failure_records:
            ts = record.telemetry_summary or {}
            if isinstance(ts, dict) and ts.get("wns") is not None and ts["wns"] < -10:
                outliers += 1
        return {"status": "OUTLIERS_DETECTED", "count": outliers}
