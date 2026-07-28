module fir_top (
    input wire clk,
    input wire rst_n,
    input wire [7:0] data_in,
    output reg [7:0] data_out
);
    reg [7:0] delay [3:0];
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i=0; i<4; i=i+1) delay[i] <= 8'd0;
            data_out <= 8'd0;
        end else begin
            delay[0] <= data_in;
            for (i=1; i<4; i=i+1) delay[i] <= delay[i-1];
            data_out <= delay[0] + delay[1] + delay[2] + delay[3];
        end
    end
endmodule
