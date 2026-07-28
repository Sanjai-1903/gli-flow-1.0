# PicoRV32 Timing Constraints for GLI-FLOW
# Target: 50 MHz (20 ns period) in SKY130

# Clock definition
create_clock -name clk -period 20.0 [get_ports clk]

# Input delays: memory interface inputs
set_input_delay -clock clk -max 2.0 [get_ports {mem_ready}]
set_input_delay -clock clk -min 0.5 [get_ports {mem_ready}]
set_input_delay -clock clk -max 3.0 [get_ports {mem_rdata}]
set_input_delay -clock clk -min 1.0 [get_ports {mem_rdata}]

# Output delays: memory interface outputs
set_output_delay -clock clk -max 4.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]
set_output_delay -clock clk -min 1.0 [get_ports {mem_valid mem_instr mem_addr mem_wdata mem_wstrb}]

# Look-ahead memory interface outputs
set_output_delay -clock clk -max 4.0 [get_ports {mem_la_read mem_la_write mem_la_addr mem_la_wdata mem_la_wstrb}]
set_output_delay -clock clk -min 1.0 [get_ports {mem_la_read mem_la_write mem_la_addr mem_la_wdata mem_la_wstrb}]

# False paths: trap output (not timing critical)
set_false_path -to [get_ports trap]

# False paths: PCPI interface (unused)
set_false_path -from [get_ports pcpi_wr]
set_false_path -from [get_ports pcpi_rd]
set_false_path -from [get_ports pcpi_wait]
set_false_path -from [get_ports pcpi_ready]
set_false_path -to [get_ports pcpi_valid]
set_false_path -to [get_ports pcpi_insn]

# False paths: IRQ interface (unused)
set_false_path -from [get_ports irq]
set_false_path -to [get_ports eoi]

# False paths: Trace interface (debug only)
set_false_path -to [get_ports trace_valid]
set_false_path -to [get_ports trace_data]

# False paths: Formal interface (debug only)
set_false_path -from [get_ports rvfi_*]
set_false_path -to [get_ports rvfi_*]
