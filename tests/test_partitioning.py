import tempfile
from pathlib import Path

from gli_flow.backends.openroad_adapter import HierarchicalBlock, HierarchicalPartitionResult
from gli_flow.telemetry.parser import TelemetryParser


def test_hierarchical_block_dataclass():
    b = HierarchicalBlock(name="cpu_core", instance_count=5000, x=0.0, y=0.0, width=300.0, height=200.0)
    assert b.name == "cpu_core"
    assert b.instance_count == 5000


def test_hierarchical_partition_result_dataclass():
    blocks = [HierarchicalBlock("cpu", 5000), HierarchicalBlock("mem", 3000)]
    r = HierarchicalPartitionResult(total_blocks=2, blocks=blocks)
    assert r.total_blocks == 2
    assert len(r.blocks) == 2


def test_hierarchical_partition_result_empty():
    r = HierarchicalPartitionResult(total_blocks=0, blocks=[])
    assert r.total_blocks == 0


def test_parse_hierarchical_partition_report_with_data():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "partition_log.txt"
        report.write_text("Partition: cpu_core instances 5000\nPartition: mem_subsystem instances 3000\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_hierarchical_partition_report(str(report))
        assert metrics["hp_total_blocks"] >= 2


def test_parse_hierarchical_partition_report_empty():
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "partition_log.txt"
        report.write_text("No partitions defined\n")
        p = TelemetryParser(tmp)
        metrics = p.parse_hierarchical_partition_report(str(report))
        assert metrics["hp_total_blocks"] == 0


def test_parse_hierarchical_partition_report_file_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        p = TelemetryParser(tmp)
        metrics = p.parse_hierarchical_partition_report(str(Path(tmp) / "nonexistent.txt"))
        assert metrics["hp_total_blocks"] == 0
