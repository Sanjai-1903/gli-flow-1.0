# SDC constraints for gcd design
create_clock -name clk -period 10.000 [get_ports clk]
set_input_delay -clock clk 2.0 [get_ports "a b"]
set_output_delay -clock clk 2.0 [get_ports "gcd_out"]
set_load 0.05 [all_outputs]
set_fanout_load 4 [all_outputs]
