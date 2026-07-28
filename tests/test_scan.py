import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import ScanChain, ScanResult
from gli_flow.telemetry.parser import TelemetryParser


def test_scan_chain_dataclass():
    c = ScanChain(chain_id=0, num_flops=128, scan_in_port="SE0", scan_out_port="SO0", chain_length=128)
    assert c.chain_id == 0
    assert c.num_flops == 128
    assert c.scan_in_port == "SE0"


def test_scan_result_dataclass():
    chains = [
        ScanChain(chain_id=0, num_flops=64, scan_in_port="SE0", scan_out_port="SO0", chain_length=64),
        ScanChain(chain_id=1, num_flops=64, scan_in_port="SE1", scan_out_port="SO1", chain_length=64),
    ]
    r = ScanResult(total_flops=128, scanned_flops=128, chains=chains,
                   scan_coverage_pct=100.0, test_clk_period_ns=100.0, was_inserted=True)
    assert r.scan_coverage_pct == 100.0
    assert r.was_inserted
    assert len(r.chains) == 2


def test_scan_result_no_scan():
    r = ScanResult(total_flops=128, scanned_flops=0, chains=[],
                   scan_coverage_pct=0.0, test_clk_period_ns=100.0, was_inserted=False)
    assert r.scan_coverage_pct == 0.0
    assert not r.was_inserted


def test_parse_scan_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "scan_log.txt"
        report.write_text("Total flip-flops: 256\nScanned flip-flops: 250\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_scan_report(str(report))
        assert metrics["scan_total_flops"] == 256
        assert metrics["scan_scanned_flops"] == 250
        assert metrics["scan_coverage_pct"] == 97.65625


def test_parse_scan_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "scan_log.txt"
        report.write_text("Scan insertion skipped\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_scan_report(str(report))
        assert metrics["scan_total_flops"] == 0
        assert metrics["scan_coverage_pct"] == 0.0


def test_parse_scan_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_scan_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["scan_status"] == "NOT_RUN"
        assert metrics["scan_scanned_flops"] is None
