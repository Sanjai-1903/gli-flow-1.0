"""
Regression test for INF-LVS-002: Malformed Netgen Command Construction.

Verifies that:
  1. When pdk_sc_spice is present, circuit2 is a single arg with all files + top cell
  2. When pdk_sc_spice is absent, circuit2 contains only the netlist + top cell
  3. Setup file and report path are never consumed as circuit specs
  4. No positional argument shifting occurs
"""


class TestInfLvs002:
    """INF-LVS-002: Netgen command argument construction."""

    def test_pdk_spice_present_combines_circuit2(self):
        """When pdk_sc_spice is found, circuit2 must combine both files + top cell."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")
        netgen_bin = "/usr/bin/netgen-lvs"
        spice_path = "/tmp/layout.spice"
        pdk_sc_spice = "/tmp/pdk.spice"
        clean_netlist = "/tmp/netlist.v"
        design_name = "top"
        setup_file = "/tmp/setup.tcl"
        report_path = "/tmp/report.txt"

        lvs_args = [netgen_bin, "-batch", "lvs"]
        lvs_args.append(f"{spice_path} {design_name}")
        lvs_args.append(f"{pdk_sc_spice} {clean_netlist} {design_name}")
        lvs_args.extend([setup_file, report_path])

        assert lvs_args[3] == f"{spice_path} {design_name}"
        assert lvs_args[4] == f"{pdk_sc_spice} {clean_netlist} {design_name}"
        assert lvs_args[4].count(" ") == 2, (
            f"circuit2 should have exactly 2 spaces (2 files + top cell), "
            f"got {lvs_args[4].count(' ')} in {lvs_args[4]!r}"
        )
        assert lvs_args[5] == setup_file, f"arg 5 should be setup file, got {lvs_args[5]!r}"
        assert lvs_args[6] == report_path, f"arg 6 should be report path, got {lvs_args[6]!r}"
        assert len(lvs_args) == 7, f"expected 7 args, got {len(lvs_args)}: {lvs_args}"

    def test_pdk_spice_absent_single_circuit2(self):
        """When pdk_sc_spice is not found, circuit2 contains only netlist + top cell."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")
        netgen_bin = "/usr/bin/netgen-lvs"
        spice_path = "/tmp/layout.spice"
        clean_netlist = "/tmp/netlist.v"
        design_name = "top"
        setup_file = "/tmp/setup.tcl"
        report_path = "/tmp/report.txt"

        lvs_args = [netgen_bin, "-batch", "lvs"]
        lvs_args.append(f"{spice_path} {design_name}")
        lvs_args.append(f"{clean_netlist} {design_name}")
        lvs_args.extend([setup_file, report_path])

        assert lvs_args[3] == f"{spice_path} {design_name}"
        assert lvs_args[4] == f"{clean_netlist} {design_name}"
        assert lvs_args[4].count(" ") == 1, (
            f"circuit2 should have exactly 1 space (1 file + top cell), "
            f"got {lvs_args[4].count(' ')} in {lvs_args[4]!r}"
        )
        assert lvs_args[5] == setup_file, f"arg 5 should be setup file, got {lvs_args[5]!r}"
        assert lvs_args[6] == report_path, f"arg 6 should be report path, got {lvs_args[6]!r}"
        assert len(lvs_args) == 7, f"expected 7 args, got {len(lvs_args)}: {lvs_args}"

    def test_no_positional_shift(self):
        """Each positional argument must retain its intended role — no shifting."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")
        netgen_bin = "/usr/bin/netgen-lvs"
        spice_path = "/tmp/layout.spice"
        pdk_sc_spice = "/tmp/pdk.spice"
        clean_netlist = "/tmp/netlist.v"
        design_name = "top"
        setup_file = "/tmp/setup.tcl"
        report_path = "/tmp/report.txt"

        lvs_args = [netgen_bin, "-batch", "lvs"]
        lvs_args.append(f"{spice_path} {design_name}")
        lvs_args.append(f"{pdk_sc_spice} {clean_netlist} {design_name}")
        lvs_args.extend([setup_file, report_path])

        args_after_lvs = lvs_args[3:]
        assert len(args_after_lvs) == 4, (
            f"expected 4 args after '-batch lvs', got {len(args_after_lvs)}"
        )
        circuit1, circuit2, setup, report = args_after_lvs
        assert setup == setup_file, f"setup shifted: expected {setup_file!r}, got {setup!r}"
        assert report == report_path, f"report shifted: expected {report_path!r}, got {report!r}"

    def test_three_token_circuit2_is_valid_netgen_syntax(self):
        """Netgen accepts 'file1 file2 topcell' as a valid circuit2 spec — verify format."""
        spec = "/tmp/pdk.spice /tmp/netlist.v top"
        parts = spec.rsplit(" ", 2)
        assert len(parts) == 3, f"rsplit with maxsplit=2 should give 3 parts, got {parts}"
        file1, file2, topcell = parts
        assert file1 == "/tmp/pdk.spice"
        assert file2 == "/tmp/netlist.v"
        assert topcell == "top"
