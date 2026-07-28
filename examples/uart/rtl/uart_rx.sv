module uart_rx (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       rx_serial,
    output logic       rx_valid,
    output logic [7:0] rx_data
);
    localparam integer CLKS_PER_BIT = 868;
    localparam integer CLKS_HALF_BIT = 434;

    typedef enum logic [2:0] {
        IDLE,
        START_BIT,
        DATA_BITS,
        STOP_BIT
    } state_t;

    state_t state;
    logic [9:0] clk_count;
    logic [2:0] bit_index;
    logic [7:0] data_reg;
    logic       rx_meta;
    logic       rx_sync;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_meta <= 1'b1;
            rx_sync <= 1'b1;
        end else begin
            rx_meta <= rx_serial;
            rx_sync <= rx_meta;
        end
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= IDLE;
            rx_valid  <= 1'b0;
            rx_data   <= 0;
            clk_count <= 0;
            bit_index <= 0;
            data_reg  <= 0;
        end else begin
            case (state)
                IDLE: begin
                    rx_valid  <= 1'b0;
                    clk_count <= 0;
                    bit_index <= 0;
                    if (rx_sync == 1'b0)
                        state <= START_BIT;
                end

                START_BIT: begin
                    if (clk_count == CLKS_HALF_BIT) begin
                        if (rx_sync == 1'b0) begin
                            clk_count <= 0;
                            state     <= DATA_BITS;
                        end else begin
                            state <= IDLE;
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                    end
                end

                DATA_BITS: begin
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                    end else begin
                        clk_count <= 0;
                        data_reg[bit_index] <= rx_sync;
                        if (bit_index < 3'd7) begin
                            bit_index <= bit_index + 1;
                        end else begin
                            bit_index <= 0;
                            state     <= STOP_BIT;
                        end
                    end
                end

                STOP_BIT: begin
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                    end else begin
                        clk_count <= 0;
                        rx_valid  <= 1'b1;
                        rx_data   <= data_reg;
                        state     <= IDLE;
                    end
                end
            endcase
        end
    end
endmodule
