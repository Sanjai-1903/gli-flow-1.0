module uart_rx (
	clk,
	rst_n,
	rx_serial,
	rx_valid,
	rx_data
);
	input wire clk;
	input wire rst_n;
	input wire rx_serial;
	output reg rx_valid;
	output reg [7:0] rx_data;
	localparam integer CLKS_PER_BIT = 868;
	localparam integer CLKS_HALF_BIT = 434;
	reg [2:0] state;
	reg [9:0] clk_count;
	reg [2:0] bit_index;
	reg [7:0] data_reg;
	reg rx_meta;
	reg rx_sync;
	always @(posedge clk or negedge rst_n)
		if (!rst_n) begin
			rx_meta <= 1'b1;
			rx_sync <= 1'b1;
		end
		else begin
			rx_meta <= rx_serial;
			rx_sync <= rx_meta;
		end
	always @(posedge clk or negedge rst_n)
		if (!rst_n) begin
			state <= 3'd0;
			rx_valid <= 1'b0;
			rx_data <= 0;
			clk_count <= 0;
			bit_index <= 0;
			data_reg <= 0;
		end
		else
			case (state)
				3'd0: begin
					rx_valid <= 1'b0;
					clk_count <= 0;
					bit_index <= 0;
					if (rx_sync == 1'b0)
						state <= 3'd1;
				end
				3'd1:
					if (clk_count == CLKS_HALF_BIT) begin
						if (rx_sync == 1'b0) begin
							clk_count <= 0;
							state <= 3'd2;
						end
						else
							state <= 3'd0;
					end
					else
						clk_count <= clk_count + 1;
				3'd2:
					if (clk_count < (CLKS_PER_BIT - 1))
						clk_count <= clk_count + 1;
					else begin
						clk_count <= 0;
						data_reg[bit_index] <= rx_sync;
						if (bit_index < 3'd7)
							bit_index <= bit_index + 1;
						else begin
							bit_index <= 0;
							state <= 3'd3;
						end
					end
				3'd3:
					if (clk_count < (CLKS_PER_BIT - 1))
						clk_count <= clk_count + 1;
					else begin
						clk_count <= 0;
						rx_valid <= 1'b1;
						rx_data <= data_reg;
						state <= 3'd0;
					end
			endcase
endmodule