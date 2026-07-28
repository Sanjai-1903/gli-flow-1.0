from gli_flow.pdk.base import PDK
from gli_flow.pdk.corner import PVTCorner
from gli_flow.pdk.registry import register_pdk


class GF180MCUPDK(PDK):
    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get("name", "gf180mcu"),
            variant=kwargs.get("variant", "gf180mcuC"),
            description="GlobalFoundries 180nm MCU open-source PDK",
            version="latest",
            vendor="GlobalFoundries / Google",
            orfs_platform="gf180mcuC",
            volare_pdk_name="gf180mcu",
            default_voltage=1.8,
            power_net_name="VDD",
            ground_net_name="VSS",
            nominal_voltage=3.3,
            track_height=12,
            metal_layers=["met1", "met2", "met3", "met4"],
            via_layers=["via1", "via2", "via3"],
            min_temperature=-40,
            max_temperature=125,
            min_voltage=1.62,
            max_voltage=1.98,
            corners=self._default_corners(),
            magic_tech_file=kwargs.get("magic_tech_file", "$PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.tech"),
            magic_rcfile=kwargs.get("magic_rcfile", "$PDK_ROOT/gf180mcuD/libs.tech/magic/gf180mcuD.magicrc"),
            netgen_setup_file=kwargs.get("netgen_setup_file", "$PDK_ROOT/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl"),
            fill_rules_file=kwargs.get("fill_rules_file", "$PDK_ROOT/gf180mcuD/libs.ref/tech/gf180mcuD/fill.json"),
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
            "worst": "gf180mcu_fd_sc_mcu7t5t__ss_125C_1v62",
            "typical": "gf180mcu_fd_sc_mcu7t5t__tt_25C_1v80",
            "best": "gf180mcu_fd_sc_mcu7t5t__ff_40C_1v95",
        }
        return mapping.get(corner.name, mapping["typical"])

    def generate_config_mk(self, design_name: str, corner: PVTCorner = None) -> str:
        corner = corner or self.typical_corner()
        lib = self.lib_set(corner)
        return f"""export DESIGN_NAME  = {design_name}
export DESIGN_NICKNAME = {design_name}
export PLATFORM     = {self.orfs_platform}

export VERILOG_FILES = $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/*.v
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc

export CORE_UTILIZATION = 30
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 2
export TNS_END_PERCENT = 100

# PVT Corner: {corner.name} ({corner.process.value}, {corner.voltage}V, {corner.temperature}C)
export CORNER = {corner.lib_suffix()}
export LIB_SYNTH = $(OBJECTS_DIR)/{lib}.lib_{corner.lib_suffix()}
export LIB_FASTEST = $(OBJECTS_DIR)/{lib}.lib_{corner.lib_suffix()}
export LIB_SLOWEST = $(OBJECTS_DIR)/{lib}.lib_{corner.lib_suffix()}
"""


register_pdk("gf180mcu", GF180MCUPDK)
