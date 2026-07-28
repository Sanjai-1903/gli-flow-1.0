module uart_tx (
	clk,
	rst_n,
	tx_start,
	tx_data,
	tx_busy,
	tx_serial
);
	input wire clk;
	input wire rst_n;
	input wire tx_start;
	input wire [7:0] tx_data;
	output reg tx_busy;
	output reg tx_serial;
	localparam integer CLKS_PER_BIT = 868;
	reg [2:0] state;
	reg [9:0] clk_count;
	reg [2:0] bit_index;
	reg [7:0] data_reg;
	always @(posedge clk or negedge rst_n)
		if (!rst_n) begin
			state <= 3'd0;
			tx_serial <= 1'b1;
			tx_busy <= 1'b0;
			clk_count <= 0;
			bit_index <= 0;
			data_reg <= 0;
		end
		else
			case (state)
				3'd0: begin
					tx_serial <= 1'b1;
					tx_busy <= 1'b0;
					clk_count <= 0;
					bit_index <= 0;
					if (tx_start) begin
						data_reg <= tx_data;
						state <= 3'd1;
						tx_busy <= 1'b1;
					end
				end
				3'd1: begin
					tx_serial <= 1'b0;
					if (clk_count < (CLKS_PER_BIT - 1))
						clk_count <= clk_count + 1;
					else begin
						clk_count <= 0;
						state <= 3'd2;
					end
				end
				3'd2: begin
					tx_serial <= data_reg[bit_index];
					if (clk_count < (CLKS_PER_BIT - 1))
						clk_count <= clk_count + 1;
					else begin
						clk_count <= 0;
						if (bit_index < 3'd7)
							bit_index <= bit_index + 1;
						else begin
							bit_index <= 0;
							state <= 3'd3;
						end
					end
				end
				3'd3: begin
					tx_serial <= 1'b1;
					if (clk_count < (CLKS_PER_BIT - 1))
						clk_count <= clk_count + 1;
					else begin
						clk_count <= 0;
						tx_busy <= 1'b0;
						state <= 3'd0;
					end
				end
			endcase
endmodule