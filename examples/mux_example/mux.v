module mux (
    input  wire        clk,
    input  wire        rst,
    input  wire [1:0]  sel,
    input  wire [7:0]  in0,
    input  wire [7:0]  in1,
    input  wire [7:0]  in2,
    input  wire [7:0]  in3,
    output reg  [7:0]  out
);

    reg [7:0] mux_out;

    always @(*) begin
        case (sel)
            2'b00:   mux_out = in0;
            2'b01:   mux_out = in1;
            2'b10:   mux_out = in2;
            default: mux_out = in3;
        endcase
    end

    always @(posedge clk or posedge rst) begin
        if (rst)
            out <= 8'b0;
        else
            out <= mux_out;
    end

endmodule
