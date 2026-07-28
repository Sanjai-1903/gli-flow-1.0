from gli_flow.pdk.base import PDK
from gli_flow.pdk.corner import PVTCorner
from gli_flow.pdk.registry import register_pdk


class IHP_SG13G2PDK(PDK):
    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get("name", "ihp-sg13g2"),
            variant=kwargs.get("variant", "sg13g2"),
            description="IHP 130nm BiCMOS open-source PDK (SG13G2)",
            version="latest",
            vendor="IHP Microelectronics",
            orfs_platform="sg13g2",
            volare_pdk_name="sg13g2",
            default_voltage=1.2,
            power_net_name="VDD",
            ground_net_name="VSS",
            nominal_voltage=1.2,
            track_height=12,
            metal_layers=["met1", "met2", "met3", "met4", "met5"],
            via_layers=["via1", "via2", "via3", "via4"],
            min_temperature=-40,
            max_temperature=125,
            min_voltage=1.08,
            max_voltage=1.32,
            corners=self._default_corners(),
            magic_tech_file=kwargs.get("magic_tech_file", "$PDK_ROOT/sg13g2/libs.tech/magic/sg13g2.tech"),
            magic_rcfile=kwargs.get("magic_rcfile", "$PDK_ROOT/sg13g2/libs.tech/magic/sg13g2.magicrc"),
            netgen_setup_file=kwargs.get("netgen_setup_file", "$PDK_ROOT/sg13g2/libs.tech/netgen/sg13g2_setup.tcl"),
            fill_rules_file=kwargs.get("fill_rules_file", "$PDK_ROOT/sg13g2/libs.ref/tech/sg13g2/fill.json"),
            liberty_file=kwargs.get("liberty_file", "$PDK_ROOT/sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_tt_025C_1v20.lib"),
        )

    def _default_corners(self):
        from gli_flow.pdk.corner import PVTCorner, CornerType, ProcessCorner
        return [
            PVTCorner(
                name="worst", corner_type=CornerType.WORST,
                process=ProcessCorner.SLOW,
                voltage=1.08, temperature=125,
            ),
            PVTCorner(
                name="typical", corner_type=CornerType.TYPICAL,
                process=ProcessCorner.TYPICAL,
                voltage=1.20, temperature=25,
            ),
            PVTCorner(
                name="best", corner_type=CornerType.BEST,
                process=ProcessCorner.FAST,
                voltage=1.32, temperature=-40,
            ),
        ]

    def lib_set(self, corner: PVTCorner) -> str:
        mapping = {
            "worst": "sg13g2_stdcell_ss_100C_1v08",
            "typical": "sg13g2_stdcell_tt_025C_1v20",
            "best": "sg13g2_stdcell_ff_100C_1v32",
        }
        return mapping.get(corner.name, mapping["typical"])

    def generate_config_mk(self, design_name: str, corner: PVTCorner = None) -> str:
        from gli_flow.pdk.corner import CornerType
        corner = corner or self.typical_corner()
        lib = self.lib_set(corner)
        return f"""export DESIGN_NAME  = {design_name}
export DESIGN_NICKNAME = {design_name}
export PLATFORM     = {self.orfs_platform}

export VERILOG_FILES = $(CURDIR)/designs/src/$(DESIGN_NICKNAME)/*.v
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


register_pdk("ihp-sg13g2", IHP_SG13G2PDK)
