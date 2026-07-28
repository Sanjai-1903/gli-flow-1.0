module uart_top (
	clk,
	rst_n,
	rx_serial,
	tx_serial,
	leds
);
	input wire clk;
	input wire rst_n;
	input wire rx_serial;
	output wire tx_serial;
	output wire [7:0] leds;
	wire loopback_start;
	wire [7:0] loopback_data;
	wire loopback_busy;
	wire rx_valid;
	uart_rx rx_inst(
		.clk(clk),
		.rst_n(rst_n),
		.rx_serial(rx_serial),
		.rx_valid(rx_valid),
		.rx_data(leds)
	);
	assign loopback_start = rx_valid & ~loopback_busy;
	assign loopback_data = leds;
	uart_tx tx_inst(
		.clk(clk),
		.rst_n(rst_n),
		.tx_start(loopback_start),
		.tx_data(loopback_data),
		.tx_busy(loopback_busy),
		.tx_serial(tx_serial)
	);
endmodule