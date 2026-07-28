import inspect

from gli_flow.core import orchestrator
from gli_flow.core.orchestrator import FlowOrchestrator


def test_orchestrator_imports():
    assert FlowOrchestrator is not None


def test_orchestrator_init_signature():
    sig = inspect.signature(FlowOrchestrator.__init__)
    params = list(sig.parameters.keys())
    assert "design_path" in params, f"expected design_path in {params}"
    assert "self" in params


def test_stages_defined():
    assert hasattr(orchestrator, "STAGES")
    assert len(orchestrator.STAGES) > 0
