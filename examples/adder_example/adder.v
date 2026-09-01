module adder (
    input  wire        clk,
    input  wire        rst,
    input  wire [3:0]  a,
    input  wire [3:0]  b,
    input  wire        cin,
    output reg  [3:0]  sum,
    output reg         cout
);

    reg [3:0] a_q, b_q;
    reg       cin_q;
    wire [4:0] result;

    assign result = a_q + b_q + cin_q;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            a_q  <= 4'b0;
            b_q  <= 4'b0;
            cin_q <= 1'b0;
            sum  <= 4'b0;
            cout <= 1'b0;
        end else begin
            a_q   <= a;
            b_q   <= b;
            cin_q <= cin;
            sum   <= result[3:0];
            cout  <= result[4];
        end
    end

endmodule
