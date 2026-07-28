//////////////////////////////////////////////////////////////////////////////
// PE (Processing Element) — 8b signed × 8b signed → 32b accumulate
// Weight-stationary: weight loads once, input/data flows W→E, psum flows N→S
// 3-stage pipeline: (1) multiply, (2) accumulate, (3) output register
//////////////////////////////////////////////////////////////////////////////
module pe #(
    parameter  DW = 8,              // input data width
    parameter  PW = 16,             // product width  (DW*2)
    parameter  AW = 32              // accumulator width
)(
    input  logic          clk,
    input  logic          rst_n,
    input  logic          clk_en,           // clock gating enable

    // Weight load interface
    input  logic          weight_load_en,
    input  logic [DW-1:0] weight_in,
    output logic [DW-1:0] weight_out,       // chain to next PE (south)

    // Data input (from west)
    input  logic          data_valid,
    input  logic [DW-1:0] data_in,
    output logic          data_valid_out,
    output logic [DW-1:0] data_out,         // to east

    // Partial sum (from north)
    input  logic          psum_valid,
    input  logic [AW-1:0] psum_in,
    output logic          psum_valid_out,
    output logic [AW-1:0] psum_out          // to south
);

    //-----------------------------------------------------------
    // Registered weight (stationary)
    //-----------------------------------------------------------
    logic [DW-1:0] weight_q;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            weight_q <= '0;
        else if (weight_load_en)
            weight_q <= weight_in;
    end
    assign weight_out = weight_q;       // chain to PE below

    //-----------------------------------------------------------
    // Pipeline stage 1: Multiply (registered)
    //-----------------------------------------------------------
    logic [PW-1:0] product;
    logic [DW-1:0] data_q;
    logic          data_valid_q;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            product      <= '0;
            data_q       <= '0;
            data_valid_q <= 1'b0;
        end else if (clk_en) begin
            product      <= $signed(data_in) * $signed(weight_q);
            data_q       <= data_in;
            data_valid_q <= data_valid;
        end
    end

    //-----------------------------------------------------------
    // Pipeline stage 2: Accumulate (registered)
    //-----------------------------------------------------------
    logic [AW-1:0] acc;
    logic          pvalid_q1;
    logic [DW-1:0] data_q2;
    logic          data_valid_q2;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            acc            <= '0;
            pvalid_q1      <= 1'b0;
            data_q2        <= '0;
            data_valid_q2  <= 1'b0;
        end else if (clk_en) begin
            if (psum_valid)
                acc <= $signed(psum_in) + $signed(product);
            else
                acc <= $signed(acc) + $signed(product);

            pvalid_q1      <= data_valid_q;   // psum valid one cycle after product
            data_q2        <= data_q;
            data_valid_q2  <= data_valid_q;
        end
    end

    //-----------------------------------------------------------
    // Pipeline stage 3: Output register (cleanup timing)
    //-----------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            psum_out       <= '0;
            psum_valid_out <= 1'b0;
            data_out       <= '0;
            data_valid_out <= 1'b0;
        end else if (clk_en) begin
            psum_out       <= acc;
            psum_valid_out <= pvalid_q1;
            data_out       <= data_q2;
            data_valid_out <= data_valid_q2;
        end
    end

endmodule
