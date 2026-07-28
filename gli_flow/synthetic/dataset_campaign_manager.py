from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid
import datetime

from gli_flow.synthetic.golden_designs import GoldenDesign, SyntheticDatasetManager
from gli_flow.synthetic.failure_injector import FailureInjector, InjectionConfig, InjectionType, INJECTION_TYPES
from gli_flow.synthetic.campaign_runner import CampaignRunner, CampaignResult, SyntheticRunResult
from gli_flow.synthetic.dataset_records import TrainingDataset

@dataclass
class CampaignMetadata:
    """
    Stores metadata for a dataset generation campaign.
    """
    campaign_name: str
    campaign_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    end_time: Optional[str] = None
    status: str = "RUNNING" # RUNNING, COMPLETED, FAILED
    target_designs: List[str] = field(default_factory=list)
    total_runs_planned: int = 0
    total_runs_executed: int = 0
    failure_injection_types: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    generated_dataset_summary: Dict[str, Any] = field(default_factory=dict)
    
class DatasetCampaignManager:
    """
    Orchestrates single, batch, and distributed campaigns for dataset generation.
    """
    def __init__(
        self,
        synthetic_dataset_manager: SyntheticDatasetManager,
        failure_injector: FailureInjector,
        campaign_runner: CampaignRunner,
    ):
        self.synthetic_dataset_manager = synthetic_dataset_manager
        self.failure_injector = failure_injector
        self.campaign_runner = campaign_runner
        self.campaign_metadata: Dict[str, CampaignMetadata] = {}

    def _initialize_campaign(
        self, campaign_name: str, target_designs: List[str], total_runs_planned: int,
        failure_injection_types: Optional[List[InjectionType]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> CampaignMetadata:
        """Initializes a new campaign and stores its metadata."""
        meta = CampaignMetadata(
            campaign_name=campaign_name,
            target_designs=target_designs,
            total_runs_planned=total_runs_planned,
            failure_injection_types=[inj.name for inj in failure_injection_types] if failure_injection_types else [],
            parameters=parameters if parameters else {}
        )
        self.campaign_metadata[meta.campaign_id] = meta
        print(f"Initialized campaign: {meta.campaign_name} (ID: {meta.campaign_id})")
        return meta

    def _finalize_campaign(self, campaign_id: str, status: str, generated_dataset_summary: Dict[str, Any]):
        """Finalizes a campaign and updates its metadata."""
        if campaign_id in self.campaign_metadata:
            meta = self.campaign_metadata[campaign_id]
            meta.end_time = datetime.datetime.now().isoformat()
            meta.status = status
            meta.generated_dataset_summary = generated_dataset_summary
            print(f"Finalized campaign: {meta.campaign_name} with status {status}")
        else:
            print(f"Warning: Campaign ID {campaign_id} not found for finalization.")

    def run_single_campaign(
        self,
        design_name: str,
        num_variations: int,
        injection_types: Optional[List[InjectionType]] = None,
        base_seed: Optional[int] = None,
        campaign_name: str = "Single Campaign",
        num_workers: int = 1, # New parameter
    ) -> TrainingDataset:
        """
        Runs a single campaign for a specific design.
        """
        design = self.synthetic_dataset_manager.get_design(design_name)
        if not design:
            raise ValueError(f"Design '{design_name}' not found.")

        meta = self._initialize_campaign(
            campaign_name=campaign_name,
            target_designs=[design_name],
            total_runs_planned=num_variations,
            failure_injection_types=injection_types,
            parameters={"num_variations": num_variations, "base_seed": base_seed, "num_workers": num_workers}
        )

        campaign_result = self.campaign_runner.run_campaign(
            design=design,
            num_variations=num_variations,
            injection_types=injection_types,
            base_seed=base_seed,
            num_workers=num_workers, # Pass num_workers
        )

        training_dataset = TrainingDataset()
        # Placeholder: Convert campaign_result into various TrainingDataset records
        # This logic will be more detailed in later phases (e.g., Phase 5, 6, 7)
        for run_res in campaign_result.results:
            # Example: Convert SyntheticRunResult to FailureTrainingRecord
            if run_res.status == "FAILURE" and run_res.injection_config:
                from gli_flow.synthetic.dataset_records import FailureTrainingRecord # Lazy import to avoid circular dependency
                failure_data = {
                    "failure_type": run_res.injection_config.injection_type.name,
                    "tool": "simulated_tool", # Placeholder
                    "stage": "simulated_stage", # Placeholder
                    "telemetry_summary": run_res.telemetry_summary,
                    "root_cause": run_res.root_cause if run_res.root_cause else "UNKNOWN",
                    "resolution": run_res.resolution_candidate if run_res.resolution_candidate else "NONE",
                    "trust_score": 0.5 # Placeholder
                }
                failure_record = FailureTrainingRecord(
                    failure_fingerprint=FailureTrainingRecord.calculate_fingerprint(failure_data),
                    **failure_data
                )
                training_dataset.failure_records.append(failure_record)
            # Add logic for ResolutionTrainingRecord, QoRTrainingRecord, GraphTrainingRecord

        meta.total_runs_executed = campaign_result.total_runs
        self._finalize_campaign(meta.campaign_id, "COMPLETED", {"failure_records": len(training_dataset.failure_records)})
        
        return training_dataset

    def run_batch_campaign(self, campaign_name: str, designs_config: Dict[str, Any], num_workers: int = 1) -> Dict[str, TrainingDataset]:
        """
        Runs multiple single campaigns in sequence.
        `designs_config` is a dictionary where keys are design names and values are dicts
        with 'num_variations', 'injection_types', 'base_seed'.
        """
        print(f"Starting batch campaign: {campaign_name}")
        all_designs = list(designs_config.keys())
        total_runs_planned = sum(d_cfg.get("num_variations", 0) for d_cfg in designs_config.values())
        meta = self._initialize_campaign(
            campaign_name=campaign_name,
            target_designs=all_designs,
            total_runs_planned=total_runs_planned,
            parameters={"designs_config": designs_config}
        )

        batch_results: Dict[str, TrainingDataset] = {}
        total_executed_runs = 0
        for design_name, config in designs_config.items():
            print(f"  Running sub-campaign for design: {design_name}")
            dataset = self.run_single_campaign(
                design_name=design_name,
                num_variations=config.get("num_variations", 1),
                injection_types=config.get("injection_types"),
                base_seed=config.get("base_seed"),
                campaign_name=f"{campaign_name} - {design_name}",
                num_workers=num_workers, # Pass num_workers to single campaign
            )
            batch_results[design_name] = dataset
            total_executed_runs += config.get("num_variations", 0) # This should come from campaign_result

        meta.total_runs_executed = total_executed_runs
        self._finalize_campaign(meta.campaign_id, "COMPLETED", {"batch_results_count": len(batch_results)})
        return batch_results

    def run_distributed_campaign(self, campaign_name: str, global_config: Dict[str, Any]) -> str:
        """
        Placeholder for orchestrating a distributed campaign.
        This would involve distributing tasks to multiple workers/machines.
        """
        print(f"Starting distributed campaign: {campaign_name} (Placeholder)")
        meta = self._initialize_campaign(
            campaign_name=campaign_name,
            target_designs=global_config.get("designs", []),
            total_runs_planned=global_config.get("total_runs_planned", 0),
            failure_injection_types=[InjectionType[it] for it in global_config.get("injection_types_names", [])],
            parameters=global_config
        )
        
        # In a real scenario, this would trigger a distributed system
        # For now, simulate some work and finalize
        import time
        time.sleep(2)
        meta.total_runs_executed = meta.total_runs_planned
        self._finalize_campaign(meta.campaign_id, "COMPLETED", {"note": "Distributed campaign simulated"})
        return meta.campaign_id