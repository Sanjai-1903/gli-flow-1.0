//////////////////////////////////////////////////////////////////////////////
// 4×4 Systolic MAC Array — Top-level Wrapper
//
// Weight-stationary topology (Kung 1982):
//   Weights pre-loaded via column broadcast (weight_in + weight_col_sel)
//   Input matrix A enters left edge: row i → PE[i][0] → shifts East
//   Partial sums accumulate North→South
//   Result matrix C exits bottom edge
//
// Latency: 3 (PE pipe) + 4 (rows) + 4 (cols) ≈ 11 cycles to first result
//
// Weight load protocol (4 cycles):
//   Set weight_col_sel=0, drive col-0 weights on weight_in, pulse weight_shift_en
//   Repeat for col_sel=1,2,3 — all 4 rows in column load simultaneously
//   → 16 weights loaded in 4 cycles
//
// Data timing:
//   data_valid pulses for each column of A.
//   data_in_row0..3 carry A[0..3][col] for the current column.
//   Internal PE pipeline creates natural skew.
//////////////////////////////////////////////////////////////////////////////
module systolic_array_4x4 #(
    parameter DW = 8,
    parameter AW = 32
)(
    input  logic          clk,
    input  logic          rst_n,

    // Weight Load
    input  logic          weight_shift_en,
    input  logic [1:0]    weight_col_sel,
    input  logic [DW-1:0] weight_in,

    // Data inputs
    input  logic          data_valid,
    input  logic [DW-1:0] data_in_row0,
    input  logic [DW-1:0] data_in_row1,
    input  logic [DW-1:0] data_in_row2,
    input  logic [DW-1:0] data_in_row3,

    // Results
    output logic          result_valid,
    output logic [AW-1:0] result_0,
    output logic [AW-1:0] result_1,
    output logic [AW-1:0] result_2,
    output logic [AW-1:0] result_3
);

    // Weight column select
    logic wl_col0, wl_col1, wl_col2, wl_col3;
    always_comb begin
        wl_col0 = weight_shift_en && (weight_col_sel == 2'd0);
        wl_col1 = weight_shift_en && (weight_col_sel == 2'd1);
        wl_col2 = weight_shift_en && (weight_col_sel == 2'd2);
        wl_col3 = weight_shift_en && (weight_col_sel == 2'd3);
    end

    // Interconnect: data valid (row 0..3, col 0..4)
    logic          dv_r0c0, dv_r0c1, dv_r0c2, dv_r0c3, dv_r0c4;
    logic          dv_r1c0, dv_r1c1, dv_r1c2, dv_r1c3, dv_r1c4;
    logic          dv_r2c0, dv_r2c1, dv_r2c2, dv_r2c3, dv_r2c4;
    logic          dv_r3c0, dv_r3c1, dv_r3c2, dv_r3c3, dv_r3c4;

    // Interconnect: data value
    logic [DW-1:0] d_r0c0, d_r0c1, d_r0c2, d_r0c3, d_r0c4;
    logic [DW-1:0] d_r1c0, d_r1c1, d_r1c2, d_r1c3, d_r1c4;
    logic [DW-1:0] d_r2c0, d_r2c1, d_r2c2, d_r2c3, d_r2c4;
    logic [DW-1:0] d_r3c0, d_r3c1, d_r3c2, d_r3c3, d_r3c4;

    // Interconnect: psum valid (row 0..4, col 0..3)
    logic          pv_r0c0, pv_r0c1, pv_r0c2, pv_r0c3;
    logic          pv_r1c0, pv_r1c1, pv_r1c2, pv_r1c3;
    logic          pv_r2c0, pv_r2c1, pv_r2c2, pv_r2c3;
    logic          pv_r3c0, pv_r3c1, pv_r3c2, pv_r3c3;
    logic          pv_r4c0, pv_r4c1, pv_r4c2, pv_r4c3;

    // Interconnect: psum value
    logic [AW-1:0] p_r0c0, p_r0c1, p_r0c2, p_r0c3;
    logic [AW-1:0] p_r1c0, p_r1c1, p_r1c2, p_r1c3;
    logic [AW-1:0] p_r2c0, p_r2c1, p_r2c2, p_r2c3;
    logic [AW-1:0] p_r3c0, p_r3c1, p_r3c2, p_r3c3;
    logic [AW-1:0] p_r4c0, p_r4c1, p_r4c2, p_r4c3;

    //-----------------------------------------------------------
    // Left-edge inputs
    //-----------------------------------------------------------
    assign dv_r0c0 = data_valid;
    assign d_r0c0  = data_in_row0;
    assign dv_r1c0 = data_valid;
    assign d_r1c0  = data_in_row1;
    assign dv_r2c0 = data_valid;
    assign d_r2c0  = data_in_row2;
    assign dv_r3c0 = data_valid;
    assign d_r3c0  = data_in_row3;

    //-----------------------------------------------------------
    // Top-edge psums = zero
    //-----------------------------------------------------------
    assign pv_r0c0 = 1'b0;
    assign p_r0c0  = '0;
    assign pv_r0c1 = 1'b0;
    assign p_r0c1  = '0;
    assign pv_r0c2 = 1'b0;
    assign p_r0c2  = '0;
    assign pv_r0c3 = 1'b0;
    assign p_r0c3  = '0;

    //-----------------------------------------------------------
    // PE array
    //-----------------------------------------------------------
    // Row 0
    pe #(.DW(DW), .AW(AW)) u_pe_r0c0 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col0), .weight_in, .weight_out(),
        .data_valid(dv_r0c0), .data_in(d_r0c0),
        .data_valid_out(dv_r0c1), .data_out(d_r0c1),
        .psum_valid(pv_r0c0), .psum_in(p_r0c0),
        .psum_valid_out(pv_r1c0), .psum_out(p_r1c0)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r0c1 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col1), .weight_in, .weight_out(),
        .data_valid(dv_r0c1), .data_in(d_r0c1),
        .data_valid_out(dv_r0c2), .data_out(d_r0c2),
        .psum_valid(pv_r0c1), .psum_in(p_r0c1),
        .psum_valid_out(pv_r1c1), .psum_out(p_r1c1)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r0c2 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col2), .weight_in, .weight_out(),
        .data_valid(dv_r0c2), .data_in(d_r0c2),
        .data_valid_out(dv_r0c3), .data_out(d_r0c3),
        .psum_valid(pv_r0c2), .psum_in(p_r0c2),
        .psum_valid_out(pv_r1c2), .psum_out(p_r1c2)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r0c3 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col3), .weight_in, .weight_out(),
        .data_valid(dv_r0c3), .data_in(d_r0c3),
        .data_valid_out(dv_r0c4), .data_out(d_r0c4),
        .psum_valid(pv_r0c3), .psum_in(p_r0c3),
        .psum_valid_out(pv_r1c3), .psum_out(p_r1c3)
    );

    // Row 1
    pe #(.DW(DW), .AW(AW)) u_pe_r1c0 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col0), .weight_in, .weight_out(),
        .data_valid(dv_r1c0), .data_in(d_r1c0),
        .data_valid_out(dv_r1c1), .data_out(d_r1c1),
        .psum_valid(pv_r1c0), .psum_in(p_r1c0),
        .psum_valid_out(pv_r2c0), .psum_out(p_r2c0)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r1c1 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col1), .weight_in, .weight_out(),
        .data_valid(dv_r1c1), .data_in(d_r1c1),
        .data_valid_out(dv_r1c2), .data_out(d_r1c2),
        .psum_valid(pv_r1c1), .psum_in(p_r1c1),
        .psum_valid_out(pv_r2c1), .psum_out(p_r2c1)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r1c2 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col2), .weight_in, .weight_out(),
        .data_valid(dv_r1c2), .data_in(d_r1c2),
        .data_valid_out(dv_r1c3), .data_out(d_r1c3),
        .psum_valid(pv_r1c2), .psum_in(p_r1c2),
        .psum_valid_out(pv_r2c2), .psum_out(p_r2c2)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r1c3 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col3), .weight_in, .weight_out(),
        .data_valid(dv_r1c3), .data_in(d_r1c3),
        .data_valid_out(dv_r1c4), .data_out(d_r1c4),
        .psum_valid(pv_r1c3), .psum_in(p_r1c3),
        .psum_valid_out(pv_r2c3), .psum_out(p_r2c3)
    );

    // Row 2
    pe #(.DW(DW), .AW(AW)) u_pe_r2c0 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col0), .weight_in, .weight_out(),
        .data_valid(dv_r2c0), .data_in(d_r2c0),
        .data_valid_out(dv_r2c1), .data_out(d_r2c1),
        .psum_valid(pv_r2c0), .psum_in(p_r2c0),
        .psum_valid_out(pv_r3c0), .psum_out(p_r3c0)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r2c1 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col1), .weight_in, .weight_out(),
        .data_valid(dv_r2c1), .data_in(d_r2c1),
        .data_valid_out(dv_r2c2), .data_out(d_r2c2),
        .psum_valid(pv_r2c1), .psum_in(p_r2c1),
        .psum_valid_out(pv_r3c1), .psum_out(p_r3c1)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r2c2 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col2), .weight_in, .weight_out(),
        .data_valid(dv_r2c2), .data_in(d_r2c2),
        .data_valid_out(dv_r2c3), .data_out(d_r2c3),
        .psum_valid(pv_r2c2), .psum_in(p_r2c2),
        .psum_valid_out(pv_r3c2), .psum_out(p_r3c2)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r2c3 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col3), .weight_in, .weight_out(),
        .data_valid(dv_r2c3), .data_in(d_r2c3),
        .data_valid_out(dv_r2c4), .data_out(d_r2c4),
        .psum_valid(pv_r2c3), .psum_in(p_r2c3),
        .psum_valid_out(pv_r3c3), .psum_out(p_r3c3)
    );

    // Row 3
    pe #(.DW(DW), .AW(AW)) u_pe_r3c0 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col0), .weight_in, .weight_out(),
        .data_valid(dv_r3c0), .data_in(d_r3c0),
        .data_valid_out(dv_r3c1), .data_out(d_r3c1),
        .psum_valid(pv_r3c0), .psum_in(p_r3c0),
        .psum_valid_out(pv_r4c0), .psum_out(p_r4c0)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r3c1 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col1), .weight_in, .weight_out(),
        .data_valid(dv_r3c1), .data_in(d_r3c1),
        .data_valid_out(dv_r3c2), .data_out(d_r3c2),
        .psum_valid(pv_r3c1), .psum_in(p_r3c1),
        .psum_valid_out(pv_r4c1), .psum_out(p_r4c1)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r3c2 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col2), .weight_in, .weight_out(),
        .data_valid(dv_r3c2), .data_in(d_r3c2),
        .data_valid_out(dv_r3c3), .data_out(d_r3c3),
        .psum_valid(pv_r3c2), .psum_in(p_r3c2),
        .psum_valid_out(pv_r4c2), .psum_out(p_r4c2)
    );
    pe #(.DW(DW), .AW(AW)) u_pe_r3c3 (
        .clk, .rst_n, .clk_en(1'b1),
        .weight_load_en(wl_col3), .weight_in, .weight_out(),
        .data_valid(dv_r3c3), .data_in(d_r3c3),
        .data_valid_out(dv_r3c4), .data_out(d_r3c4),
        .psum_valid(pv_r3c3), .psum_in(p_r3c3),
        .psum_valid_out(pv_r4c3), .psum_out(p_r4c3)
    );

    //-----------------------------------------------------------
    // Output capture
    //-----------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            result_valid <= 1'b0;
            result_0     <= '0;
            result_1     <= '0;
            result_2     <= '0;
            result_3     <= '0;
        end else begin
            result_valid <= pv_r4c0 | pv_r4c1 | pv_r4c2 | pv_r4c3;
            result_0     <= p_r4c0;
            result_1     <= p_r4c1;
            result_2     <= p_r4c2;
            result_3     <= p_r4c3;
        end
    end

endmodule
