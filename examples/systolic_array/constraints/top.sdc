# ============================================================
# SDC Constraints — 4x4 Systolic Array @ 100 MHz (10 ns)
# ============================================================
set PERIOD 10.0

# Master clock
create_clock -name clk -period $PERIOD [get_ports clk]
set_clock_uncertainty 0.5 [get_clocks clk]
set_clock_transition  0.3 [get_clocks clk]
set_clock_latency     1.0 [get_clocks clk]

# Input delays (50% of period)
set_input_delay  -clock clk 5.0 [all_inputs]
set_output_delay -clock clk 5.0 [all_outputs]

# False paths: reset is async, no timing arc needed
set_false_path -reset_path [get_ports rst_n]

# Max fanout / transition
set_max_fanout 8 [current_design]
set_max_transition 0.5 [current_design]

# Operating conditions
set_operating_conditions -max_library sky130_fd_sc_hd__ss_100C_1v60 \
                         -min_library sky130_fd_sc_hd__ff_100C_1v95 \
                         -max ss_100C_1v60 \
                         -min ff_100C_1v95
