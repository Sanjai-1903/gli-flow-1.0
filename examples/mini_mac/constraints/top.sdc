create_clock -name clk -period 20.0 [get_ports clk]
set_clock_uncertainty 1.0 [get_clocks clk]
set_input_delay -clock clk -max 2.0 [get_ports rst_n]
set_output_delay -clock clk -max 2.0 [all_outputs]
