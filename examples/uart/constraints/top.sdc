# ============================================================
# SDC Constraints — UART Loopback @ 100 MHz (10 ns)
# Target: sky130 (SkyWater 130nm)
# ============================================================

set PERIOD 10.0

# ------------------------------------------------------------
# Clock
# ------------------------------------------------------------
create_clock -name clk -period $PERIOD [get_ports clk]
set_clock_uncertainty 0.5 [get_clocks clk]
set_clock_transition  0.3 [get_clocks clk]
set_clock_latency     1.0 [get_clocks clk]

# ------------------------------------------------------------
# Input delays (50% of period)
# ------------------------------------------------------------
set_input_delay  -clock clk 5.0 [get_ports rx_serial]
set_input_delay  -clock clk 5.0 [get_ports rst_n]

# ------------------------------------------------------------
# Output delays (50% of period)
# ------------------------------------------------------------
set_output_delay -clock clk 5.0 [get_ports tx_serial]
set_output_delay -clock clk 5.0 [get_ports leds]

# ------------------------------------------------------------
# False paths
# ------------------------------------------------------------
# Async reset — no reset-to-output timing arc needed
set_false_path -reset_path [get_ports rst_n]

# rx_serial is asynchronous to clk (UART oversampling domain)
set_false_path -from [get_ports rx_serial]

# ------------------------------------------------------------
# Drive strength and loading
# ------------------------------------------------------------
set_drive 1 [get_ports clk]
set_load 0.05 [get_ports tx_serial]
set_load 0.05 [get_ports leds]

# ------------------------------------------------------------
# Physical constraints
# ------------------------------------------------------------
set_max_fanout 8 [current_design]
set_max_transition 0.5 [current_design]

# Operating conditions are managed by ORFS platform config
