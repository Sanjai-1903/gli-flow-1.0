import os
import json
import shutil

from pathlib import Path

TINYTAPEOUT_TEMPLATE = {
    "name": "tinytapeout",
    "description": "TinyTapeout shuttle-compatible template — 2x2 tile with 8 IOs",
    "default_pdk": "sky130",
    "default_pdk_variant": "sky130A",
    "top_module": "tt_um_design",
    "clock_port": "clk",
    "clock_period_ns": 10.0,
    "io_constraints": {
        "input_pins": ["ui_in[7:0]"],
        "output_pins": ["uo_out[7:0]"],
        "bidirectional_pins": ["uio_in[7:0]", "uio_out[7:0]", "uio_oe[7:0]"],
        "extra_ports": ["ena", "rst_n", "clk"]
    },
    "die_area": "0 0 200 200",
    "core_utilization": 30,
    "generated_sdc": (
        "create_clock -name clk -period 10.0 [get_ports clk]\n"
        "set_clock_uncertainty 1.0 [get_clocks clk]\n"
        "set_input_delay -clock clk -max 2.0 [get_ports ena]\n"
        "set_input_delay -clock clk -max 2.0 [get_ports rst_n]\n"
        "set_input_delay -clock clk -max 2.0 [get_ports ui_in*]\n"
        "set_input_delay -clock clk -max 2.0 [get_ports uio_in*]\n"
        "set_output_delay -clock clk -max 2.0 [get_ports uo_out*]\n"
        "set_output_delay -clock clk -max 2.0 [get_ports uio_out*]\n"
        "set_output_delay -clock clk -max 2.0 [get_ports uio_oe*]\n"
    ),
    "manifest_template": {
        "design_name": "${design_name}",
        "rtl_files": ["${design_dir}/rtl/${design_name}.v"],
        "top_module": "tt_um_${design_name}",
        "backend": "openroad",
        "pdk": "${pdk}",
        "pdk_variant": "${pdk_variant}",
        "clock_port": "clk",
        "clock_period_ns": 10.0,
        "constraints": ["${design_dir}/constraints/top.sdc"],
        "threads": 4,
        "mode": "tinytapeout",
        "die_area": "0 0 200 200",
        "core_utilization": 30,
        "corners": [
            {"name": "worst", "type": "worst", "process": "slow", "voltage": 1.62, "temperature": 125},
            {"name": "typical", "type": "typical", "process": "typical", "voltage": 1.80, "temperature": 25},
            {"name": "best", "type": "best", "process": "fast", "voltage": 1.95, "temperature": -40}
        ]
    }
}


def scaffold_tinytapeout_design(design_name: str, output_dir: str, pdk: str = "sky130", pdk_variant: str = "sky130A"):
    out = Path(output_dir)
    rtl_dir = out / "rtl"
    constraints_dir = out / "constraints"
    rtl_dir.mkdir(parents=True, exist_ok=True)
    constraints_dir.mkdir(parents=True, exist_ok=True)

    top_sv = f"""module tt_um_{design_name} (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);
    // User design goes here
    assign uo_out = ui_in;
    assign uio_out = 8'b0;
    assign uio_oe = 8'b0;
endmodule
"""
    (rtl_dir / f"{design_name}.v").write_text(top_sv)

    sdc = TINYTAPEOUT_TEMPLATE["generated_sdc"]
    (constraints_dir / "top.sdc").write_text(sdc)

    manifest = dict(TINYTAPEOUT_TEMPLATE["manifest_template"])
    manifest["design_name"] = design_name
    manifest["pdk"] = pdk
    manifest["pdk_variant"] = pdk_variant
    manifest["rtl_files"] = [f"examples/{design_name}/rtl/{design_name}.v"]

    manifest_path = out / "gli_manifest.yaml"
    yaml_lines = []
    for k, v in manifest.items():
        if isinstance(v, list):
            yaml_lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    yaml_lines.append(f"  - {{")
                    for ik, iv in item.items():
                        yaml_lines.append(f"      {ik}: {iv}")
                    yaml_lines.append(f"    }}")
                else:
                    yaml_lines.append(f"  - {item}")
        elif isinstance(v, dict):
            yaml_lines.append(f"{k}:")
            for sk, sv in v.items():
                yaml_lines.append(f"  {sk}: {sv}")
        elif isinstance(v, str) and v.startswith("${"):
            yaml_lines.append(f"# {k}: {v}  # populated by template")
        else:
            yaml_lines.append(f"{k}: {v}")
    manifest_path.write_text("\n".join(yaml_lines) + "\n")

    return str(manifest_path)


def detect_mode_from_manifest(manifest: dict) -> str:
    mode = manifest.get("mode", "standard")
    if mode == "tinytapeout":
        return "tinytapeout"
    top = manifest.get("top_module", "")
    if top.startswith("tt_um_"):
        return "tinytapeout"
    return "standard"
