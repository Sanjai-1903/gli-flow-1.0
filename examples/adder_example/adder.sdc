# 100 MHz clock (10 ns period) on the clk port
create_clock -name clk -period 10.000 [get_ports clk]

set_input_delay  -clock clk 2.0 [get_ports {a[*] b[*] cin rst}]
set_output_delay -clock clk 2.0 [get_ports {sum[*] cout}]

set_load 0.05 [all_outputs]
