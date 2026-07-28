from pathlib import Path

from gli_flow.core.orchestrator import SignoffGate


def test_missing_drc_blocks_success():
    gate = SignoffGate()
    gate.synth_ok = gate.gds_present = gate.def_present = gate.netlist_present = True
    gate.setup_pass = gate.hold_pass = True
    gate.lvs_pass = gate.antenna_pass = gate.density_pass = True
    gate.magic_drc_pass = False
    gate.klayout_drc_pass = False
    assert gate.tapeout_ready == False
    assert "DRC" in " ".join(gate.blocking_failures())


def test_violated_setup_blocks_success():
    gate = SignoffGate()
    for field in gate.__dataclass_fields__:
        setattr(gate, field, True)
    gate.setup_pass = False
    assert gate.tapeout_ready == False


def test_synthetic_antenna_zero_is_gone():
    src = Path("gli_flow/backends/openroad_adapter.py").read_text()
    assert "Total violations: 0" not in src
    assert 'write("Total violations' not in src
