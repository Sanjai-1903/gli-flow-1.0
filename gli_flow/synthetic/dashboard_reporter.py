from gli_flow.synthetic.golden_designs import SyntheticDatasetManager, GOLDEN_DESIGNS
from gli_flow.synthetic.failure_injector import FailureInjector, InjectionType, InjectionConfig
from gli_flow.synthetic.campaign_runner import CampaignRunner, SyntheticRunResult
from gli_flow.synthetic.dataset_records import TrainingDataset, FailureTrainingRecord, ResolutionTrainingRecord
from gli_flow.synthetic.quality_engine import QualityEngine

import random
from typing import Dict, Any, List

class DashboardReporter:
    """
    Generates summary statistics for the synthetic dataset dashboard.
    """
    def __init__(self, dataset: TrainingDataset):
        self.dataset = dataset

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Calculates and returns a dictionary of metrics for the dashboard.
        """
        generated_runs = len(self.dataset.failure_records) # Assuming each failure record corresponds to a run
        
        unique_failures = set()
        for record in self.dataset.failure_records:
            unique_failures.add(record.failure_fingerprint)
        num_unique_failures = len(unique_failures)

        unique_resolutions = set()
        for record in self.dataset.resolution_records:
            unique_resolutions.add(record.fix_applied) # Assuming fix_applied is unique enough
        num_unique_resolutions = len(unique_resolutions)

        # Placeholder for Atlas Coverage Growth, Trust Distribution, Dataset Size
        # These would require more sophisticated logic and historical data
        atlas_coverage_growth = "N/A (requires historical data)"
        trust_distribution = {"min": 0.0, "max": 1.0, "avg": sum(r.trust_score for r in self.dataset.failure_records if r.trust_score is not None) / num_unique_failures if num_unique_failures > 0 else 0.0}
        dataset_size = {
            "failure_records": len(self.dataset.failure_records),
            "resolution_records": len(self.dataset.resolution_records),
            "qor_records": len(self.dataset.qor_records),
            "graph_records": len(self.dataset.graph_records),
            "total_records": len(self.dataset.failure_records) + len(self.dataset.resolution_records) + len(self.dataset.qor_records) + len(self.dataset.graph_records),
        }

        return {
            "generated_runs": generated_runs,
            "unique_failures": num_unique_failures,
            "unique_resolutions": num_unique_resolutions,
            "atlas_coverage_growth": atlas_coverage_growth,
            "trust_distribution": trust_distribution,
            "dataset_size": dataset_size,
        }

def generate_sample_dashboard_data():
    """
    Generates sample data and reports dashboard metrics.
    """
    print("Generating sample dashboard data...")
    synthetic_dataset_manager = SyntheticDatasetManager()
    failure_injector = FailureInjector()
    campaign_runner = CampaignRunner(failure_injector)
    quality_engine = QualityEngine()

    # Create a new, empty TrainingDataset to populate
    training_dataset = TrainingDataset()

    # Run a small campaign
    design_to_test = synthetic_dataset_manager.get_design("picorv32")
    if design_to_test:
        campaign_result = campaign_runner.run_campaign(
            design=design_to_test,
            num_variations=10,
            injection_types=[InjectionType.CLOCK_PERIOD_SWEEP, InjectionType.ROUTING_CONGESTION],
            base_seed=123
        )

        # Process campaign results into FailureTrainingRecords and ResolutionTrainingRecords
        for run_res in campaign_result.results:
            # Create FailureTrainingRecord
            if run_res.status == "FAILURE":
                failure_data = {
                    "failure_type": run_res.injection_config.injection_type.name if run_res.injection_config else "UNKNOWN",
                    "tool": "simulated_tool",
                    "stage": "simulated_stage",
                    "telemetry_summary": run_res.telemetry_summary,
                    "root_cause": run_res.root_cause,
                    "resolution": run_res.resolution_candidate,
                    "trust_score": random.uniform(0.5, 1.0) # Simulate trust score
                }
                failure_record = FailureTrainingRecord(
                    failure_fingerprint=FailureTrainingRecord.calculate_fingerprint(failure_data),
                    **failure_data
                )
                training_dataset.failure_records.append(failure_record)

                # Create ResolutionTrainingRecord for failures
                if run_res.resolution_candidate:
                    resolution_record = ResolutionTrainingRecord(
                        failure_fingerprint=failure_record.failure_fingerprint,
                        fix_applied=run_res.resolution_candidate,
                        outcome="FIX_ATTEMPTED_RESULT", # Placeholder, would be actual outcome
                        metrics_after_fix={"sim_qor_after_fix": run_res.qor * 1.1} # Simulate improvement
                    )
                    training_dataset.resolution_records.append(resolution_record)
            
            # For successful runs without explicit failure injection, we might still have QoR records
            # Or if a campaign variation led to success after a theoretical fix
            # This is simplified for demonstration
            # In a full system, QoR records would be generated more systematically


    # Perform quality checks on the generated dataset
    quality_report = quality_engine.perform_quality_checks(training_dataset)
    print("
Quality Report:")
    print(quality_report)

    # Generate dashboard metrics
    reporter = DashboardReporter(training_dataset)
    metrics = reporter.get_dashboard_metrics()

    print("
--- Synthetic Dataset Dashboard Metrics ---")
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"- {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"- {key}: {value}")

if __name__ == "__main__":
    generate_sample_dashboard_data()
