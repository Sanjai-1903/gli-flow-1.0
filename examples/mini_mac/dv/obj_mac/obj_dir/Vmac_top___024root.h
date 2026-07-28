// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design internal header
// See Vmac_top.h for the primary calling header

#ifndef VERILATED_VMAC_TOP___024ROOT_H_
#define VERILATED_VMAC_TOP___024ROOT_H_  // guard

#include "verilated.h"


class Vmac_top__Syms;

class alignas(VL_CACHE_LINE_BYTES) Vmac_top___024root final : public VerilatedModule {
  public:

    // DESIGN SPECIFIC STATE
    // Anonymous structures to workaround compiler member-count bugs
    struct {
        VL_IN8(clk,0,0);
        VL_IN8(rst_n,0,0);
        VL_IN8(psel,0,0);
        VL_IN8(penable,0,0);
        VL_IN8(pwrite,0,0);
        VL_OUT8(pready,0,0);
        VL_OUT8(done_o,0,0);
        VL_OUT8(fsm_state_o,2,0);
        VL_OUT8(m_req_o,0,0);
        VL_IN8(m_gnt_i,0,0);
        VL_OUT8(m_we_o,0,0);
        VL_IN8(m_rvalid_i,0,0);
        CData/*0:0*/ mac_top__DOT__start;
        CData/*7:0*/ mac_top__DOT__reg_m;
        CData/*7:0*/ mac_top__DOT__reg_k;
        CData/*7:0*/ mac_top__DOT__reg_n;
        CData/*0:0*/ mac_top__DOT__load_wgt;
        CData/*3:0*/ mac_top__DOT__state;
        CData/*3:0*/ mac_top__DOT__next_state;
        CData/*1:0*/ mac_top__DOT__wgt_cnt;
        CData/*1:0*/ mac_top__DOT__res_cnt;
        CData/*7:0*/ mac_top__DOT__row_cnt;
        CData/*3:0*/ mac_top__DOT__feed_cnt;
        CData/*3:0*/ mac_top__DOT__drain_cnt;
        CData/*0:0*/ mac_top__DOT__wgt_done_r;
        CData/*0:0*/ mac_top__DOT__res_done_r;
        CData/*0:0*/ mac_top__DOT__m_req_c;
        CData/*0:0*/ mac_top__DOT__m_we_c;
        CData/*0:0*/ mac_top__DOT__u_regs__DOT__sticky_done;
        CData/*3:0*/ mac_top__DOT__u_regs__DOT__pe_addr_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg;
    };
    struct {
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        CData/*7:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg;
        CData/*0:0*/ __VstlFirstIteration;
        CData/*0:0*/ __VicoFirstIteration;
        CData/*0:0*/ __Vtrigprevexpr___TOP__clk__0;
        CData/*0:0*/ __Vtrigprevexpr___TOP__rst_n__0;
        CData/*0:0*/ __VactContinue;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg;
        SData/*15:0*/ mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg;
        VL_IN(paddr,31,0);
        VL_IN(pwdata,31,0);
        VL_OUT(prdata,31,0);
        VL_OUT(m_addr_o,31,0);
        VL_OUT(m_wdata_o,31,0);
        VL_IN(m_rdata_i,31,0);
        VL_OUT(result_hold_o_0,31,0);
        VL_OUT(result_hold_o_1,31,0);
        VL_OUT(result_hold_o_2,31,0);
        VL_OUT(result_hold_o_3,31,0);
        IData/*31:0*/ mac_top__DOT__wgt_addr;
        IData/*31:0*/ mac_top__DOT__act_addr;
        IData/*31:0*/ mac_top__DOT__res_addr;
        IData/*31:0*/ mac_top__DOT__m_addr_c;
        IData/*31:0*/ mac_top__DOT__m_wdata_c;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    };
    struct {
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
        IData/*31:0*/ __VactIterCount;
        VlUnpacked<VlUnpacked<CData/*7:0*/, 4>, 4> mac_top__DOT__wgt_buf;
        VlUnpacked<VlUnpacked<CData/*7:0*/, 4>, 4> mac_top__DOT__weight_in;
        VlUnpacked<CData/*7:0*/, 4> mac_top__DOT__act_buf;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__res_buf;
        VlUnpacked<CData/*7:0*/, 4> mac_top__DOT__row_in;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__col_in;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__col_out;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__result_hold;
        VlUnpacked<CData/*7:0*/, 4> mac_top__DOT__u_array__DOT__row_in;
        VlUnpacked<VlUnpacked<CData/*7:0*/, 4>, 4> mac_top__DOT__u_array__DOT__weight_in;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__u_array__DOT__col_in;
        VlUnpacked<IData/*31:0*/, 4> mac_top__DOT__u_array__DOT__col_out;
        VlUnpacked<VlUnpacked<CData/*7:0*/, 5>, 4> mac_top__DOT__u_array__DOT__h_wire;
        VlUnpacked<VlUnpacked<IData/*31:0*/, 4>, 5> mac_top__DOT__u_array__DOT__v_wire;
        VlUnpacked<CData/*0:0*/, 2> __Vm_traceActivity;
    };
    VlTriggerVec<1> __VstlTriggered;
    VlTriggerVec<1> __VicoTriggered;
    VlTriggerVec<1> __VactTriggered;
    VlTriggerVec<1> __VnbaTriggered;

    // INTERNAL VARIABLES
    Vmac_top__Syms* const vlSymsp;

    // CONSTRUCTORS
    Vmac_top___024root(Vmac_top__Syms* symsp, const char* v__name);
    ~Vmac_top___024root();
    VL_UNCOPYABLE(Vmac_top___024root);

    // INTERNAL METHODS
    void __Vconfigure(bool first);
};


#endif  // guard
