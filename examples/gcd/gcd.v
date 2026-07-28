module gcd (
    input wire clk,
    input wire rst,
    input wire start,
    input wire [7:0] a,
    input wire [7:0] b,
    output reg [7:0] result,
    output reg done
);

reg [7:0] x;
reg [7:0] y;
reg running;

always @(posedge clk) begin

    if (rst) begin
        x <= 0;
        y <= 0;
        result <= 0;
        done <= 0;
        running <= 0;
    end

    else if (start && !running) begin
        x <= a;
        y <= b;
        done <= 0;
        running <= 1;
    end

    else if (running) begin

        if (x == y) begin
            result <= x;
            done <= 1;
            running <= 0;
        end

        else if (x > y) begin
            x <= x - y;
        end

        else begin
            y <= y - x;
        end
    end
end

endmodule
