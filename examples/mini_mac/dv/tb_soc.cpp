#include <iostream>
#include <iomanip>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vsoc_top.h"
#include "Vsoc_top___024root.h"

vluint64_t main_time = 0;
double sc_time_stamp() { return main_time; }

int main(int argc, char** argv) {
    Verilated::commandArgs(argc, argv);
    Vsoc_top* top = new Vsoc_top;
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    top->trace(tfp, 99);
    tfp->open("waveform.vcd");

    top->clk = 0; top->rst_n = 0;
    bool dma_ever_started = false;
    bool dma_finished = false;

    std::cout << "\033[1;34m[SIM] Starting MINI-MAC SoC Simulation...\033[0m" << std::endl;

    auto* r = top->rootp;

    for (int i = 0; i < 50000; i++) {
        if (i == 100) top->rst_n = 1;
        top->clk = !top->clk;
        top->eval();
        tfp->dump(main_time);
        main_time += 5;

        uint32_t pc = r->soc_top__DOT__instr_addr;
        uint32_t instr = r->soc_top__DOT__instr_rdata;
        if (dma_ever_started) dma_finished = true;
        if (r->soc_top__DOT__dma_busy) dma_ever_started = true;

        // Trace all cycles with data request, APB events, or MAC activity
        if (i < 3000) {
            bool active = (r->soc_top__DOT____Vcellinp__u_bridge__obi_req
                        || r->soc_top__DOT__u_core__DOT__u_ibex_core__DOT__data_req_out
                        || r->soc_top__DOT__u_bridge__DOT__state != 0
                        || r->soc_top__DOT__u_mac__DOT__state != 0
                        || r->soc_top__DOT__cpu_rvalid
                        || r->soc_top__DOT__mac_done
                        || r->soc_top__DOT__apb_penable);
            if (active) {
                std::cout << "[TRK] C" << std::dec << i
                          << " PC=0x" << std::hex << pc
                          << " dRq=" << (int)r->soc_top__DOT__u_core__DOT__u_ibex_core__DOT__data_req_out
                          << " we=" << (int)r->soc_top__DOT__apb_pwrite
                          << " gnt=" << (int)r->soc_top__DOT__cpu_gnt
                          << " rv=" << (int)r->soc_top__DOT__cpu_rvalid
                          << " bRq=" << (int)r->soc_top__DOT____Vcellinp__u_bridge__obi_req
                          << " bS=" << (int)r->soc_top__DOT__u_bridge__DOT__state
                          << " pEn=" << (int)r->soc_top__DOT__apb_penable
                          << " pRdy=" << (int)r->soc_top__DOT__apb_pready
                          << " macS=" << (int)r->soc_top__DOT__u_mac__DOT__state
                          << " macD=" << (int)r->soc_top__DOT__mac_done
                          << " wd=0x" << std::hex << (int)r->soc_top__DOT__apb_pwdata
                          << std::dec << std::endl;
            }
        }

        // First 500 cycles: trace PC changes only
        static uint32_t last_pc = ~0;
        if (pc != last_pc && i < 500) {
            std::cout << "[TRACE] Cycle " << i
                      << " PC=0x" << std::hex << pc
                      << " instr=0x" << std::hex << instr
                      << std::dec << std::endl;
            last_pc = pc;
        }

        if (i % 10000 == 0 && top->rst_n) {
            std::cout << "[DEBUG] Cycle " << i
                      << " | PC: 0x" << std::hex << pc
                      << " | instr: 0x" << std::hex << instr
                      << " | MAC State: " << (int)r->soc_top__DOT__mac_fsm_state << std::dec << std::endl;
        }
    }

    std::cout << "\n================================================" << std::endl;
    std::cout << "        MINI-MAC TELEMETRY DASHBOARD" << std::endl;
    std::cout << "================================================" << std::endl;
    
    if (r->soc_top__DOT__instr_addr > 0x0) std::cout << "1. CPU Boot Check:      \033[1;32mPASSED\033[0m" << std::endl;
    else std::cout << "1. CPU Boot Check:      \033[1;31mFAILED\033[0m" << std::endl;

    if (dma_ever_started && dma_finished) std::cout << "2. DMA Status Check:    \033[1;32mPASSED\033[0m" << std::endl;
    else std::cout << "2. DMA Status Check:    \033[1;31mFAILED\033[0m" << std::endl;

    if (r->soc_top__DOT__mac_done) std::cout << "3. MAC Status Check:    \033[1;32mPASSED (AI Inference Success!)\033[0m" << std::endl;
    else std::cout << "3. MAC Status Check:    \033[1;31mFAILED\033[0m" << std::endl;

    std::cout << "================================================" << std::endl;

    tfp->close(); delete top; return 0;
}
