module gpio_top (
    input wire clk,
    input wire rst_n,
    input wire [7:0] gpio_in,
    output reg [7:0] gpio_out
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            gpio_out <= 8'd0;
        else
            gpio_out <= gpio_in;
    end
endmodule
