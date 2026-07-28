from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CIConfig:
    design_path: str
    junit_output: Optional[str] = None
    markdown_output: Optional[str] = None
    baseline_run_id: Optional[str] = None
    qor_score_min: Optional[float] = None
    wns_max: Optional[float] = None
    utilization_max: Optional[float] = None
    runtime_max_sec: Optional[float] = None
    verbose: bool = False
    db_path: Optional[str] = None
