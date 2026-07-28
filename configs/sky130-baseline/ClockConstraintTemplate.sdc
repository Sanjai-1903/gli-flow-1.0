# Clock constraint template for GLI-FLOW
create_clock [get_ports {clk}] -name clk -period 10.0
set_clock_uncertainty 0.1 [get_clocks clk]
set_clock_transition 0.1 [get_clocks clk]
set_input_delay 0.5 -clock clk [all_inputs]
set_output_delay 0.5 -clock clk [all_outputs]
