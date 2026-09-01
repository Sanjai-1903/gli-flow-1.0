# 100 MHz clock (10 ns) on clk
create_clock -name clk -period 10.000 [get_ports clk]

set_input_delay  -clock clk 2.0 [get_ports {sel[*] in0[*] in1[*] in2[*] in3[*] rst}]
set_output_delay -clock clk 2.0 [get_ports {out[*]}]

set_load 0.05 [all_outputs]
