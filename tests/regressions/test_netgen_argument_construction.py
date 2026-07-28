import pytest


class TestNetgenArgumentConstruction:
    """Verify netgen -batch lvs receives correctly formed arguments."""

    def test_circuit2_combines_pdk_and_netlist(self):
        """When pdk_sc_spice is present, circuit2 must combine both + top cell."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")
        netgen_bin = "/usr/bin/netgen-lvs"
        spice_path = "/tmp/circuit1.spice"
        clean_netlist = "/tmp/netlist.v"
        design_name = "top"
        setup_file = "/tmp/setup.tcl"
        report_path = "/tmp/report.txt"
        pdk_sc_spice = "/tmp/pdk.spice"

        lvs_args = [netgen_bin, "-batch", "lvs"]
        lvs_args.append(f"{spice_path} {design_name}")
        lvs_args.append(f"{pdk_sc_spice} {clean_netlist} {design_name}")
        lvs_args.extend([setup_file, report_path])

        circuit2 = lvs_args[4]
        assert circuit2 == f"{pdk_sc_spice} {clean_netlist} {design_name}"
        assert circuit2.count(" ") == 2

    def test_each_circuit_spec_has_correct_token_count(self):
        """Circuit1 has 1 space, circuit2 has 1 or 2 spaces."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")

        # Circuit1: always "path topcell"
        c1 = "/tmp/layout.spice top"
        assert c1.count(" ") == 1

        # Circuit2 with pdk: "pdk netlist topcell"
        c2_with_pdk = "/tmp/pdk.spice /tmp/netlist.v top"
        assert c2_with_pdk.count(" ") == 2

        # Circuit2 without pdk: "netlist topcell"
        c2_without_pdk = "/tmp/netlist.v top"
        assert c2_without_pdk.count(" ") == 1

    def test_no_embedded_spaces_in_file_paths(self):
        """File paths within circuit specs must not contain spaces."""
        specs = [
            ("/tmp/circuit1.spice", "top"),
            ("/tmp/pdk_models.spice", "top"),
            ("/tmp/design_netlist.v", "top"),
        ]
        for file_part, name in specs:
            arg = f"{file_part} {name}"
            parsed_file, parsed_name = arg.rsplit(" ", 1)
            assert parsed_file == file_part
            assert parsed_name == name
            assert " " not in parsed_file

    def test_setup_and_report_not_consumed_as_circuit_specs(self):
        """Setup file and report path must remain as last 2 positional args."""
        from gli_flow.backends.openroad_adapter import OpenRoadAdapter

        adapter = OpenRoadAdapter(pdk_root="/tmp")
        netgen_bin = "/usr/bin/netgen-lvs"
        spice_path = "/tmp/circuit1.spice"
        clean_netlist = "/tmp/netlist.v"
        design_name = "top"
        setup_file = "/tmp/setup.tcl"
        report_path = "/tmp/report.txt"
        pdk_sc_spice = "/tmp/pdk.spice"

        lvs_args = [netgen_bin, "-batch", "lvs"]
        lvs_args.append(f"{spice_path} {design_name}")
        lvs_args.append(f"{pdk_sc_spice} {clean_netlist} {design_name}")
        lvs_args.extend([setup_file, report_path])

        assert lvs_args[-2] == setup_file, f"expected setup file, got {lvs_args[-2]!r}"
        assert lvs_args[-1] == report_path, f"expected report path, got {lvs_args[-1]!r}"
