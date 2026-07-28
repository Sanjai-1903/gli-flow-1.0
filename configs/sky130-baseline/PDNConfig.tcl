# PDN configuration for sky130
set ::env(VDD_NETS) [list {vdd} {VPWR}]
set ::env(GND_NETS) [list {vss} {VGND}]
set ::env(PDN_CFG) [list \
    {li1 met1} \
    {met1 met2} \
    {met2 met3} \
    {met3 met4} \
    {met4 met5} \
]
set ::env(FP_PDN_VWIDTH) 1.6
set ::env(FP_PDN_HWIDTH) 1.6
set ::env(FP_PDN_VSPACING) 5.0
set ::env(FP_PDN_HSPACING) 5.0
