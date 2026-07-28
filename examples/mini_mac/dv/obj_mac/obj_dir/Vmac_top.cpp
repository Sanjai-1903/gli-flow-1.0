// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Model implementation (design independent parts)

#include "Vmac_top__pch.h"
#include "verilated_vcd_c.h"

//============================================================
// Constructors

Vmac_top::Vmac_top(VerilatedContext* _vcontextp__, const char* _vcname__)
    : VerilatedModel{*_vcontextp__}
    , vlSymsp{new Vmac_top__Syms(contextp(), _vcname__, this)}
    , clk{vlSymsp->TOP.clk}
    , rst_n{vlSymsp->TOP.rst_n}
    , psel{vlSymsp->TOP.psel}
    , penable{vlSymsp->TOP.penable}
    , pwrite{vlSymsp->TOP.pwrite}
    , pready{vlSymsp->TOP.pready}
    , done_o{vlSymsp->TOP.done_o}
    , fsm_state_o{vlSymsp->TOP.fsm_state_o}
    , m_req_o{vlSymsp->TOP.m_req_o}
    , m_gnt_i{vlSymsp->TOP.m_gnt_i}
    , m_we_o{vlSymsp->TOP.m_we_o}
    , m_rvalid_i{vlSymsp->TOP.m_rvalid_i}
    , paddr{vlSymsp->TOP.paddr}
    , pwdata{vlSymsp->TOP.pwdata}
    , prdata{vlSymsp->TOP.prdata}
    , m_addr_o{vlSymsp->TOP.m_addr_o}
    , m_wdata_o{vlSymsp->TOP.m_wdata_o}
    , m_rdata_i{vlSymsp->TOP.m_rdata_i}
    , result_hold_o_0{vlSymsp->TOP.result_hold_o_0}
    , result_hold_o_1{vlSymsp->TOP.result_hold_o_1}
    , result_hold_o_2{vlSymsp->TOP.result_hold_o_2}
    , result_hold_o_3{vlSymsp->TOP.result_hold_o_3}
    , rootp{&(vlSymsp->TOP)}
{
    // Register model with the context
    contextp()->addModel(this);
}

Vmac_top::Vmac_top(const char* _vcname__)
    : Vmac_top(Verilated::threadContextp(), _vcname__)
{
}

//============================================================
// Destructor

Vmac_top::~Vmac_top() {
    delete vlSymsp;
}

//============================================================
// Evaluation function

#ifdef VL_DEBUG
void Vmac_top___024root___eval_debug_assertions(Vmac_top___024root* vlSelf);
#endif  // VL_DEBUG
void Vmac_top___024root___eval_static(Vmac_top___024root* vlSelf);
void Vmac_top___024root___eval_initial(Vmac_top___024root* vlSelf);
void Vmac_top___024root___eval_settle(Vmac_top___024root* vlSelf);
void Vmac_top___024root___eval(Vmac_top___024root* vlSelf);

void Vmac_top::eval_step() {
    VL_DEBUG_IF(VL_DBG_MSGF("+++++TOP Evaluate Vmac_top::eval_step\n"); );
#ifdef VL_DEBUG
    // Debug assertions
    Vmac_top___024root___eval_debug_assertions(&(vlSymsp->TOP));
#endif  // VL_DEBUG
    vlSymsp->__Vm_activity = true;
    vlSymsp->__Vm_deleter.deleteAll();
    if (VL_UNLIKELY(!vlSymsp->__Vm_didInit)) {
        vlSymsp->__Vm_didInit = true;
        VL_DEBUG_IF(VL_DBG_MSGF("+ Initial\n"););
        Vmac_top___024root___eval_static(&(vlSymsp->TOP));
        Vmac_top___024root___eval_initial(&(vlSymsp->TOP));
        Vmac_top___024root___eval_settle(&(vlSymsp->TOP));
    }
    VL_DEBUG_IF(VL_DBG_MSGF("+ Eval\n"););
    Vmac_top___024root___eval(&(vlSymsp->TOP));
    // Evaluate cleanup
    Verilated::endOfEval(vlSymsp->__Vm_evalMsgQp);
}

//============================================================
// Events and timing
bool Vmac_top::eventsPending() { return false; }

uint64_t Vmac_top::nextTimeSlot() {
    VL_FATAL_MT(__FILE__, __LINE__, "", "%Error: No delays in the design");
    return 0;
}

//============================================================
// Utilities

const char* Vmac_top::name() const {
    return vlSymsp->name();
}

//============================================================
// Invoke final blocks

void Vmac_top___024root___eval_final(Vmac_top___024root* vlSelf);

VL_ATTR_COLD void Vmac_top::final() {
    Vmac_top___024root___eval_final(&(vlSymsp->TOP));
}

//============================================================
// Implementations of abstract methods from VerilatedModel

const char* Vmac_top::hierName() const { return vlSymsp->name(); }
const char* Vmac_top::modelName() const { return "Vmac_top"; }
unsigned Vmac_top::threads() const { return 1; }
void Vmac_top::prepareClone() const { contextp()->prepareClone(); }
void Vmac_top::atClone() const {
    contextp()->threadPoolpOnClone();
}
std::unique_ptr<VerilatedTraceConfig> Vmac_top::traceConfig() const {
    return std::unique_ptr<VerilatedTraceConfig>{new VerilatedTraceConfig{false, false, false}};
};

//============================================================
// Trace configuration

void Vmac_top___024root__trace_decl_types(VerilatedVcd* tracep);

void Vmac_top___024root__trace_init_top(Vmac_top___024root* vlSelf, VerilatedVcd* tracep);

VL_ATTR_COLD static void trace_init(void* voidSelf, VerilatedVcd* tracep, uint32_t code) {
    // Callback from tracep->open()
    Vmac_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vmac_top___024root*>(voidSelf);
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    if (!vlSymsp->_vm_contextp__->calcUnusedSigs()) {
        VL_FATAL_MT(__FILE__, __LINE__, __FILE__,
            "Turning on wave traces requires Verilated::traceEverOn(true) call before time 0.");
    }
    vlSymsp->__Vm_baseCode = code;
    tracep->pushPrefix(std::string{vlSymsp->name()}, VerilatedTracePrefixType::SCOPE_MODULE);
    Vmac_top___024root__trace_decl_types(tracep);
    Vmac_top___024root__trace_init_top(vlSelf, tracep);
    tracep->popPrefix();
}

VL_ATTR_COLD void Vmac_top___024root__trace_register(Vmac_top___024root* vlSelf, VerilatedVcd* tracep);

VL_ATTR_COLD void Vmac_top::trace(VerilatedVcdC* tfp, int levels, int options) {
    if (tfp->isOpen()) {
        vl_fatal(__FILE__, __LINE__, __FILE__,"'Vmac_top::trace()' shall not be called after 'VerilatedVcdC::open()'.");
    }
    if (false && levels && options) {}  // Prevent unused
    tfp->spTrace()->addModel(this);
    tfp->spTrace()->addInitCb(&trace_init, &(vlSymsp->TOP));
    Vmac_top___024root__trace_register(&(vlSymsp->TOP), tfp->spTrace());
}
