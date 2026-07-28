from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ExecutionRecord:

    run_id: str
    design_name: str
    toolchain: str
    status: str
    current_stage: str
    progress: int = 0
    wns: Optional[float] = None
    tns: Optional[float] = None
    utilization: Optional[float] = None
    runtime_sec: Optional[float] = None
    cell_count: Optional[int] = None
    qor_score: Optional[float] = None
    hold_wns: Optional[float] = None
    hold_tns: Optional[float] = None
    run_dir: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    implementation_status: str = "NOT_STARTED"
    signoff_status: str = "NOT_RUN"
    tapeout_ready: bool = False
    implementation_score: Optional[float] = None
    signoff_score: Optional[float] = None
    signoff_classification: Optional[dict] = None

    llm_investigation_available: bool = False
    llm_investigation_status: Optional[str] = None
    llm_investigation_summary: Optional[str] = None
    llm_investigation_timestamp: Optional[str] = None
