from gli_flow.pdk.base import PDK
from gli_flow.pdk.corner import PVTCorner
from gli_flow.pdk.registry import register_pdk


class Sky130PDK(PDK):
    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get("name", "sky130"),
            variant=kwargs.get("variant", "sky130A"),
            description="SkyWater 130nm open-source PDK",
            version="latest",
            vendor="SkyWater Technology / Google",
            orfs_platform="sky130hd",
            volare_pdk_name="sky130",
            default_voltage=1.8,
            power_net_name="VDD",
            ground_net_name="VSS",
            nominal_voltage=1.8,
            track_height=14,
            metal_layers=["li1", "met1", "met2", "met3", "met4", "met5"],
            via_layers=["via", "via2", "via3", "via4"],
            min_temperature=-40,
            max_temperature=125,
            min_voltage=1.62,
            max_voltage=1.98,
            corners=self._default_corners(),
            magic_tech_file=kwargs.get("magic_tech_file", "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.tech"),
            magic_rcfile=kwargs.get("magic_rcfile", "$PDK_ROOT/sky130A/libs.tech/magic/sky130A.magicrc"),
            netgen_setup_file=kwargs.get("netgen_setup_file", "$PDK_ROOT/sky130A/libs.tech/netgen/sky130A_setup.tcl"),
            fill_rules_file=kwargs.get("fill_rules_file", "$PDK_ROOT/sky130A/libs.ref/tech/sky130A/fill.json"),
            liberty_file=kwargs.get("liberty_file", "$PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"),
        )

    def _default_corners(self):
        from gli_flow.pdk.corner import PVTCorner, CornerType, ProcessCorner
        return [
            PVTCorner(
                name="worst", corner_type=CornerType.WORST,
                process=ProcessCorner.SLOW,
                voltage=1.62, temperature=125,
            ),
            PVTCorner(
                name="typical", corner_type=CornerType.TYPICAL,
                process=ProcessCorner.TYPICAL,
                voltage=1.80, temperature=25,
            ),
            PVTCorner(
                name="best", corner_type=CornerType.BEST,
                process=ProcessCorner.FAST,
                voltage=1.95, temperature=-40,
            ),
        ]

    def lib_set(self, corner: PVTCorner) -> str:
        mapping = {
            "worst": "sky130_fd_sc_hd__ss_100C_1v60",
            "typical": "sky130_fd_sc_hd__tt_025C_1v80",
            "best": "sky130_fd_sc_hd__ff_100C_1v95",
        }
        return mapping.get(corner.name, mapping["typical"])

    def generate_config_mk(self, design_name: str, corner: PVTCorner = None) -> str:
        from gli_flow.pdk.corner import CornerType
        corner = corner or self.typical_corner()
        lib = self.lib_set(corner)
        return f"""export DESIGN_NAME  = {design_name}
export DESIGN_NICKNAME = {design_name}
export PLATFORM     = {self.orfs_platform}

export VERILOG_FILES = $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/pe.sv $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/systolic_array_4x4.sv
export SDC_FILE      = $(CURDIR)/designs/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

export CORE_UTILIZATION = 30
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 2
export TNS_END_PERCENT = 100

# PVT Corner: {corner.name} ({corner.process.value}, {corner.voltage}V, {corner.temperature}C)
export CORNER = {corner.lib_suffix()}
export LIB_SYNTH = -l $(OBJECTS_DIR)/{lib}.lib
export LIB_FASTEST = $(OBJECTS_DIR)/{lib}.lib
export LIB_SLOWEST = $(OBJECTS_DIR)/{lib}.lib
"""


register_pdk("sky130", Sky130PDK)
