create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay -clock clk 2.0 [get_ports reset]
set_output_delay -clock clk 2.0 [get_ports count]
set_load 0.05 [all_outputs]
