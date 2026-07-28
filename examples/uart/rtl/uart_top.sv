module uart_top (
    input  logic       clk,
    input  logic       rst_n,
    input  logic       rx_serial,
    output logic       tx_serial,
    output logic [7:0] leds
);
    logic       loopback_start;
    logic [7:0] loopback_data;
    logic       loopback_busy;
    logic       rx_valid;

    uart_rx rx_inst (
        .clk      (clk),
        .rst_n    (rst_n),
        .rx_serial(rx_serial),
        .rx_valid (rx_valid),
        .rx_data  (leds)
    );

    assign loopback_start = rx_valid & ~loopback_busy;
    assign loopback_data  = leds;

    uart_tx tx_inst (
        .clk      (clk),
        .rst_n    (rst_n),
        .tx_start (loopback_start),
        .tx_data  (loopback_data),
        .tx_busy  (loopback_busy),
        .tx_serial(tx_serial)
    );
endmodule
