// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vmac_top.h for the primary calling header

#include "Vmac_top__pch.h"
#include "Vmac_top___024root.h"

VL_ATTR_COLD void Vmac_top___024root___eval_static(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_static\n"); );
}

VL_ATTR_COLD void Vmac_top___024root___eval_initial__TOP(Vmac_top___024root* vlSelf);

VL_ATTR_COLD void Vmac_top___024root___eval_initial(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_initial\n"); );
    // Body
    Vmac_top___024root___eval_initial__TOP(vlSelf);
    vlSelf->__Vm_traceActivity[1U] = 1U;
    vlSelf->__Vm_traceActivity[0U] = 1U;
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = vlSelf->clk;
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = vlSelf->rst_n;
}

VL_ATTR_COLD void Vmac_top___024root___eval_initial__TOP(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_initial__TOP\n"); );
    // Body
    vlSelf->mac_top__DOT__col_in[0U] = 0U;
    vlSelf->mac_top__DOT__col_in[1U] = 0U;
    vlSelf->mac_top__DOT__col_in[2U] = 0U;
    vlSelf->mac_top__DOT__col_in[3U] = 0U;
    vlSelf->pready = 1U;
}

VL_ATTR_COLD void Vmac_top___024root___eval_final(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_final\n"); );
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__stl(Vmac_top___024root* vlSelf);
#endif  // VL_DEBUG
VL_ATTR_COLD bool Vmac_top___024root___eval_phase__stl(Vmac_top___024root* vlSelf);

VL_ATTR_COLD void Vmac_top___024root___eval_settle(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_settle\n"); );
    // Init
    IData/*31:0*/ __VstlIterCount;
    CData/*0:0*/ __VstlContinue;
    // Body
    __VstlIterCount = 0U;
    vlSelf->__VstlFirstIteration = 1U;
    __VstlContinue = 1U;
    while (__VstlContinue) {
        if (VL_UNLIKELY((0x64U < __VstlIterCount))) {
#ifdef VL_DEBUG
            Vmac_top___024root___dump_triggers__stl(vlSelf);
#endif
            VL_FATAL_MT("/home/bolter/mini_mac_soc/rtl/accel/mac_top.v", 1, "", "Settle region did not converge.");
        }
        __VstlIterCount = ((IData)(1U) + __VstlIterCount);
        __VstlContinue = 0U;
        if (Vmac_top___024root___eval_phase__stl(vlSelf)) {
            __VstlContinue = 1U;
        }
        vlSelf->__VstlFirstIteration = 0U;
    }
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__stl(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___dump_triggers__stl\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VstlTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VstlTriggered.word(0U))) {
        VL_DBG_MSGF("         'stl' region trigger index 0 is active: Internal 'stl' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vmac_top___024root___stl_sequent__TOP__0(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___stl_sequent__TOP__0\n"); );
    // Body
    vlSelf->mac_top__DOT__load_wgt = 0U;
    vlSelf->done_o = (8U == (IData)(vlSelf->mac_top__DOT__state));
    vlSelf->mac_top__DOT__m_we_c = 0U;
    vlSelf->mac_top__DOT__m_req_c = 0U;
    vlSelf->mac_top__DOT__m_wdata_c = 0U;
    vlSelf->mac_top__DOT__next_state = vlSelf->mac_top__DOT__state;
    if ((8U & (IData)(vlSelf->mac_top__DOT__state))) {
        vlSelf->mac_top__DOT__next_state = 0U;
    } else if ((4U & (IData)(vlSelf->mac_top__DOT__state))) {
        if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
            if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                vlSelf->mac_top__DOT__next_state = 
                    (((IData)(vlSelf->mac_top__DOT__row_cnt) 
                      == (0xffU & ((IData)(vlSelf->mac_top__DOT__reg_m) 
                                   - (IData)(1U))))
                      ? 8U : 3U);
            } else if (vlSelf->mac_top__DOT__res_done_r) {
                vlSelf->mac_top__DOT__next_state = 7U;
            }
        } else if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
            if ((0xaU == (IData)(vlSelf->mac_top__DOT__drain_cnt))) {
                vlSelf->mac_top__DOT__next_state = 6U;
            }
        } else if ((0xbU == (IData)(vlSelf->mac_top__DOT__feed_cnt))) {
            vlSelf->mac_top__DOT__next_state = 5U;
        }
    } else if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
        if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
            if (vlSelf->m_rvalid_i) {
                vlSelf->mac_top__DOT__next_state = 4U;
            }
        } else {
            vlSelf->mac_top__DOT__next_state = 3U;
        }
    } else if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
        if (vlSelf->mac_top__DOT__wgt_done_r) {
            vlSelf->mac_top__DOT__next_state = 2U;
        }
    } else if (vlSelf->mac_top__DOT__start) {
        vlSelf->mac_top__DOT__next_state = 1U;
    }
    vlSelf->mac_top__DOT__m_addr_c = 0U;
    vlSelf->fsm_state_o = (7U & (IData)(vlSelf->mac_top__DOT__state));
    vlSelf->result_hold_o_0 = vlSelf->mac_top__DOT__result_hold
        [0U];
    vlSelf->result_hold_o_1 = vlSelf->mac_top__DOT__result_hold
        [1U];
    vlSelf->result_hold_o_2 = vlSelf->mac_top__DOT__result_hold
        [2U];
    vlSelf->result_hold_o_3 = vlSelf->mac_top__DOT__result_hold
        [3U];
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[0U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[0U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[0U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[0U][4U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[1U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[1U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[1U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[1U][4U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[2U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[2U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[2U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[2U][4U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[3U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[3U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[3U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[3U][4U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__weight_in[0U][0U] = vlSelf->mac_top__DOT__wgt_buf
        [0U][3U];
    vlSelf->mac_top__DOT__weight_in[0U][1U] = vlSelf->mac_top__DOT__wgt_buf
        [0U][0U];
    vlSelf->mac_top__DOT__weight_in[0U][2U] = vlSelf->mac_top__DOT__wgt_buf
        [0U][1U];
    vlSelf->mac_top__DOT__weight_in[0U][3U] = vlSelf->mac_top__DOT__wgt_buf
        [0U][2U];
    vlSelf->mac_top__DOT__weight_in[1U][0U] = vlSelf->mac_top__DOT__wgt_buf
        [1U][3U];
    vlSelf->mac_top__DOT__weight_in[1U][1U] = vlSelf->mac_top__DOT__wgt_buf
        [1U][0U];
    vlSelf->mac_top__DOT__weight_in[1U][2U] = vlSelf->mac_top__DOT__wgt_buf
        [1U][1U];
    vlSelf->mac_top__DOT__weight_in[1U][3U] = vlSelf->mac_top__DOT__wgt_buf
        [1U][2U];
    vlSelf->mac_top__DOT__weight_in[2U][0U] = vlSelf->mac_top__DOT__wgt_buf
        [2U][3U];
    vlSelf->mac_top__DOT__weight_in[2U][1U] = vlSelf->mac_top__DOT__wgt_buf
        [2U][0U];
    vlSelf->mac_top__DOT__weight_in[2U][2U] = vlSelf->mac_top__DOT__wgt_buf
        [2U][1U];
    vlSelf->mac_top__DOT__weight_in[2U][3U] = vlSelf->mac_top__DOT__wgt_buf
        [2U][2U];
    vlSelf->mac_top__DOT__weight_in[3U][0U] = vlSelf->mac_top__DOT__wgt_buf
        [3U][3U];
    vlSelf->mac_top__DOT__weight_in[3U][1U] = vlSelf->mac_top__DOT__wgt_buf
        [3U][0U];
    vlSelf->mac_top__DOT__weight_in[3U][2U] = vlSelf->mac_top__DOT__wgt_buf
        [3U][1U];
    vlSelf->mac_top__DOT__weight_in[3U][3U] = vlSelf->mac_top__DOT__wgt_buf
        [3U][2U];
    vlSelf->mac_top__DOT__row_in[0U] = 0U;
    vlSelf->mac_top__DOT__row_in[1U] = 0U;
    vlSelf->mac_top__DOT__row_in[2U] = 0U;
    vlSelf->mac_top__DOT__row_in[3U] = 0U;
    if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                  >> 3U)))) {
        if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
                if ((1U & (~ (IData)(vlSelf->mac_top__DOT__state)))) {
                    vlSelf->mac_top__DOT__load_wgt = 1U;
                }
            }
        }
        if ((4U & (IData)(vlSelf->mac_top__DOT__state))) {
            if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
                if ((1U & (~ (IData)(vlSelf->mac_top__DOT__state)))) {
                    vlSelf->mac_top__DOT__m_we_c = 1U;
                    vlSelf->mac_top__DOT__m_req_c = 1U;
                    vlSelf->mac_top__DOT__m_wdata_c 
                        = vlSelf->mac_top__DOT__result_hold
                        [vlSelf->mac_top__DOT__res_cnt];
                    vlSelf->mac_top__DOT__m_addr_c 
                        = ((vlSelf->mac_top__DOT__res_addr 
                            + ((IData)(vlSelf->mac_top__DOT__row_cnt) 
                               << 4U)) + ((IData)(vlSelf->mac_top__DOT__res_cnt) 
                                          << 2U));
                }
            }
            if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                          >> 1U)))) {
                if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                    vlSelf->mac_top__DOT__row_in[0U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [0U];
                    vlSelf->mac_top__DOT__row_in[1U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [1U];
                    vlSelf->mac_top__DOT__row_in[2U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [2U];
                    vlSelf->mac_top__DOT__row_in[3U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [3U];
                } else {
                    vlSelf->mac_top__DOT__row_in[0U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [0U];
                    vlSelf->mac_top__DOT__row_in[1U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [1U];
                    vlSelf->mac_top__DOT__row_in[2U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [2U];
                    vlSelf->mac_top__DOT__row_in[3U] 
                        = vlSelf->mac_top__DOT__act_buf
                        [3U];
                }
            }
        } else if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
            if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                vlSelf->mac_top__DOT__m_we_c = 0U;
                vlSelf->mac_top__DOT__m_req_c = 1U;
                vlSelf->mac_top__DOT__m_addr_c = (vlSelf->mac_top__DOT__act_addr 
                                                  + 
                                                  (0xcU 
                                                   & ((IData)(vlSelf->mac_top__DOT__row_cnt) 
                                                      << 2U)));
            }
        } else if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
            vlSelf->mac_top__DOT__m_we_c = 0U;
            vlSelf->mac_top__DOT__m_req_c = 1U;
            vlSelf->mac_top__DOT__m_addr_c = (vlSelf->mac_top__DOT__wgt_addr 
                                              + ((IData)(vlSelf->mac_top__DOT__wgt_cnt) 
                                                 << 2U));
        }
    }
    vlSelf->mac_top__DOT__u_array__DOT__col_in[0U] 
        = vlSelf->mac_top__DOT__col_in[0U];
    vlSelf->mac_top__DOT__u_array__DOT__col_in[1U] 
        = vlSelf->mac_top__DOT__col_in[1U];
    vlSelf->mac_top__DOT__u_array__DOT__col_in[2U] 
        = vlSelf->mac_top__DOT__col_in[2U];
    vlSelf->mac_top__DOT__u_array__DOT__col_in[3U] 
        = vlSelf->mac_top__DOT__col_in[3U];
    vlSelf->m_we_o = vlSelf->mac_top__DOT__m_we_c;
    vlSelf->m_req_o = vlSelf->mac_top__DOT__m_req_c;
    vlSelf->m_wdata_o = vlSelf->mac_top__DOT__m_wdata_c;
    vlSelf->m_addr_o = vlSelf->mac_top__DOT__m_addr_c;
    vlSelf->prdata = (((((((((0U == (0xffU & vlSelf->paddr)) 
                             | (4U == (0xffU & vlSelf->paddr))) 
                            | (8U == (0xffU & vlSelf->paddr))) 
                           | (0x18U == (0xffU & vlSelf->paddr))) 
                          | (0x1cU == (0xffU & vlSelf->paddr))) 
                         | (0x20U == (0xffU & vlSelf->paddr))) 
                        | (0x24U == (0xffU & vlSelf->paddr))) 
                       | (0x28U == (0xffU & vlSelf->paddr)))
                       ? ((0U == (0xffU & vlSelf->paddr))
                           ? 0U : ((4U == (0xffU & vlSelf->paddr))
                                    ? (((IData)(vlSelf->mac_top__DOT__u_regs__DOT__sticky_done) 
                                        << 3U) | (IData)(vlSelf->fsm_state_o))
                                    : ((8U == (0xffU 
                                               & vlSelf->paddr))
                                        ? (((IData)(vlSelf->mac_top__DOT__reg_m) 
                                            << 0x10U) 
                                           | (((IData)(vlSelf->mac_top__DOT__reg_k) 
                                               << 8U) 
                                              | (IData)(vlSelf->mac_top__DOT__reg_n)))
                                        : ((0x18U == 
                                            (0xffU 
                                             & vlSelf->paddr))
                                            ? (IData)(vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg)
                                            : ((0x1cU 
                                                == 
                                                (0xffU 
                                                 & vlSelf->paddr))
                                                ? (
                                                   (2U 
                                                    & (IData)(vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg))
                                                    ? 
                                                   ((1U 
                                                     & (IData)(vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg))
                                                     ? vlSelf->result_hold_o_3
                                                     : vlSelf->result_hold_o_2)
                                                    : 
                                                   ((1U 
                                                     & (IData)(vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg))
                                                     ? vlSelf->result_hold_o_1
                                                     : vlSelf->result_hold_o_0))
                                                : (
                                                   (0x20U 
                                                    == 
                                                    (0xffU 
                                                     & vlSelf->paddr))
                                                    ? vlSelf->mac_top__DOT__wgt_addr
                                                    : 
                                                   ((0x24U 
                                                     == 
                                                     (0xffU 
                                                      & vlSelf->paddr))
                                                     ? vlSelf->mac_top__DOT__act_addr
                                                     : vlSelf->mac_top__DOT__res_addr)))))))
                       : 0U);
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[0U][0U] 
        = vlSelf->mac_top__DOT__weight_in[0U][0U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[0U][1U] 
        = vlSelf->mac_top__DOT__weight_in[0U][1U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[0U][2U] 
        = vlSelf->mac_top__DOT__weight_in[0U][2U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[0U][3U] 
        = vlSelf->mac_top__DOT__weight_in[0U][3U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[1U][0U] 
        = vlSelf->mac_top__DOT__weight_in[1U][0U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[1U][1U] 
        = vlSelf->mac_top__DOT__weight_in[1U][1U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[1U][2U] 
        = vlSelf->mac_top__DOT__weight_in[1U][2U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[1U][3U] 
        = vlSelf->mac_top__DOT__weight_in[1U][3U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[2U][0U] 
        = vlSelf->mac_top__DOT__weight_in[2U][0U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[2U][1U] 
        = vlSelf->mac_top__DOT__weight_in[2U][1U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[2U][2U] 
        = vlSelf->mac_top__DOT__weight_in[2U][2U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[2U][3U] 
        = vlSelf->mac_top__DOT__weight_in[2U][3U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[3U][0U] 
        = vlSelf->mac_top__DOT__weight_in[3U][0U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[3U][1U] 
        = vlSelf->mac_top__DOT__weight_in[3U][1U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[3U][2U] 
        = vlSelf->mac_top__DOT__weight_in[3U][2U];
    vlSelf->mac_top__DOT__u_array__DOT__weight_in[3U][3U] 
        = vlSelf->mac_top__DOT__weight_in[3U][3U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[0U] 
        = vlSelf->mac_top__DOT__row_in[0U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[1U] 
        = vlSelf->mac_top__DOT__row_in[1U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[2U] 
        = vlSelf->mac_top__DOT__row_in[2U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[3U] 
        = vlSelf->mac_top__DOT__row_in[3U];
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[0U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__col_in
        [0U];
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[0U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT__col_in
        [1U];
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[0U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT__col_in
        [2U];
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[0U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT__col_in
        [3U];
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[0U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__row_in
        [0U];
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[1U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__row_in
        [1U];
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[2U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__row_in
        [2U];
    vlSelf->mac_top__DOT__u_array__DOT__h_wire[3U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__row_in
        [3U];
    vlSelf->mac_top__DOT__u_array__DOT__col_out[0U] 
        = vlSelf->mac_top__DOT__u_array__DOT__v_wire
        [4U][0U];
    vlSelf->mac_top__DOT__u_array__DOT__col_out[1U] 
        = vlSelf->mac_top__DOT__u_array__DOT__v_wire
        [4U][1U];
    vlSelf->mac_top__DOT__u_array__DOT__col_out[2U] 
        = vlSelf->mac_top__DOT__u_array__DOT__v_wire
        [4U][2U];
    vlSelf->mac_top__DOT__u_array__DOT__col_out[3U] 
        = vlSelf->mac_top__DOT__u_array__DOT__v_wire
        [4U][3U];
    vlSelf->mac_top__DOT__col_out[3U] = vlSelf->mac_top__DOT__u_array__DOT__col_out
        [3U];
    vlSelf->mac_top__DOT__col_out[2U] = vlSelf->mac_top__DOT__u_array__DOT__col_out
        [2U];
    vlSelf->mac_top__DOT__col_out[1U] = vlSelf->mac_top__DOT__u_array__DOT__col_out
        [1U];
    vlSelf->mac_top__DOT__col_out[0U] = vlSelf->mac_top__DOT__u_array__DOT__col_out
        [0U];
}

VL_ATTR_COLD void Vmac_top___024root___eval_stl(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_stl\n"); );
    // Body
    if ((1ULL & vlSelf->__VstlTriggered.word(0U))) {
        Vmac_top___024root___stl_sequent__TOP__0(vlSelf);
        vlSelf->__Vm_traceActivity[1U] = 1U;
        vlSelf->__Vm_traceActivity[0U] = 1U;
    }
}

VL_ATTR_COLD void Vmac_top___024root___eval_triggers__stl(Vmac_top___024root* vlSelf);

VL_ATTR_COLD bool Vmac_top___024root___eval_phase__stl(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_phase__stl\n"); );
    // Init
    CData/*0:0*/ __VstlExecute;
    // Body
    Vmac_top___024root___eval_triggers__stl(vlSelf);
    __VstlExecute = vlSelf->__VstlTriggered.any();
    if (__VstlExecute) {
        Vmac_top___024root___eval_stl(vlSelf);
    }
    return (__VstlExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__ico(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___dump_triggers__ico\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VicoTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VicoTriggered.word(0U))) {
        VL_DBG_MSGF("         'ico' region trigger index 0 is active: Internal 'ico' trigger - first iteration\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__act(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___dump_triggers__act\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VactTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VactTriggered.word(0U))) {
        VL_DBG_MSGF("         'act' region trigger index 0 is active: @(posedge clk or negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__nba(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___dump_triggers__nba\n"); );
    // Body
    if ((1U & (~ (IData)(vlSelf->__VnbaTriggered.any())))) {
        VL_DBG_MSGF("         No triggers active\n");
    }
    if ((1ULL & vlSelf->__VnbaTriggered.word(0U))) {
        VL_DBG_MSGF("         'nba' region trigger index 0 is active: @(posedge clk or negedge rst_n)\n");
    }
}
#endif  // VL_DEBUG

VL_ATTR_COLD void Vmac_top___024root___ctor_var_reset(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___ctor_var_reset\n"); );
    // Body
    vlSelf->clk = VL_RAND_RESET_I(1);
    vlSelf->rst_n = VL_RAND_RESET_I(1);
    vlSelf->paddr = VL_RAND_RESET_I(32);
    vlSelf->psel = VL_RAND_RESET_I(1);
    vlSelf->penable = VL_RAND_RESET_I(1);
    vlSelf->pwrite = VL_RAND_RESET_I(1);
    vlSelf->pwdata = VL_RAND_RESET_I(32);
    vlSelf->prdata = VL_RAND_RESET_I(32);
    vlSelf->pready = VL_RAND_RESET_I(1);
    vlSelf->done_o = VL_RAND_RESET_I(1);
    vlSelf->fsm_state_o = VL_RAND_RESET_I(3);
    vlSelf->m_req_o = VL_RAND_RESET_I(1);
    vlSelf->m_gnt_i = VL_RAND_RESET_I(1);
    vlSelf->m_addr_o = VL_RAND_RESET_I(32);
    vlSelf->m_we_o = VL_RAND_RESET_I(1);
    vlSelf->m_wdata_o = VL_RAND_RESET_I(32);
    vlSelf->m_rvalid_i = VL_RAND_RESET_I(1);
    vlSelf->m_rdata_i = VL_RAND_RESET_I(32);
    vlSelf->result_hold_o_0 = VL_RAND_RESET_I(32);
    vlSelf->result_hold_o_1 = VL_RAND_RESET_I(32);
    vlSelf->result_hold_o_2 = VL_RAND_RESET_I(32);
    vlSelf->result_hold_o_3 = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__start = VL_RAND_RESET_I(1);
    vlSelf->mac_top__DOT__reg_m = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__reg_k = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__reg_n = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__wgt_addr = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__act_addr = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__res_addr = VL_RAND_RESET_I(32);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 4; ++__Vi1) {
            vlSelf->mac_top__DOT__wgt_buf[__Vi0][__Vi1] = VL_RAND_RESET_I(8);
        }
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 4; ++__Vi1) {
            vlSelf->mac_top__DOT__weight_in[__Vi0][__Vi1] = VL_RAND_RESET_I(8);
        }
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__act_buf[__Vi0] = VL_RAND_RESET_I(8);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__res_buf[__Vi0] = VL_RAND_RESET_I(32);
    }
    vlSelf->mac_top__DOT__load_wgt = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__row_in[__Vi0] = VL_RAND_RESET_I(8);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__col_in[__Vi0] = VL_RAND_RESET_I(32);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__col_out[__Vi0] = VL_RAND_RESET_I(32);
    }
    vlSelf->mac_top__DOT__state = VL_RAND_RESET_I(4);
    vlSelf->mac_top__DOT__next_state = VL_RAND_RESET_I(4);
    vlSelf->mac_top__DOT__wgt_cnt = VL_RAND_RESET_I(2);
    vlSelf->mac_top__DOT__res_cnt = VL_RAND_RESET_I(2);
    vlSelf->mac_top__DOT__row_cnt = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__feed_cnt = VL_RAND_RESET_I(4);
    vlSelf->mac_top__DOT__drain_cnt = VL_RAND_RESET_I(4);
    vlSelf->mac_top__DOT__wgt_done_r = VL_RAND_RESET_I(1);
    vlSelf->mac_top__DOT__res_done_r = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__result_hold[__Vi0] = VL_RAND_RESET_I(32);
    }
    vlSelf->mac_top__DOT__m_req_c = VL_RAND_RESET_I(1);
    vlSelf->mac_top__DOT__m_addr_c = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__m_we_c = VL_RAND_RESET_I(1);
    vlSelf->mac_top__DOT__m_wdata_c = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_regs__DOT__sticky_done = VL_RAND_RESET_I(1);
    vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg = VL_RAND_RESET_I(4);
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__u_array__DOT__row_in[__Vi0] = VL_RAND_RESET_I(8);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 4; ++__Vi1) {
            vlSelf->mac_top__DOT__u_array__DOT__weight_in[__Vi0][__Vi1] = VL_RAND_RESET_I(8);
        }
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__u_array__DOT__col_in[__Vi0] = VL_RAND_RESET_I(32);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        vlSelf->mac_top__DOT__u_array__DOT__col_out[__Vi0] = VL_RAND_RESET_I(32);
    }
    for (int __Vi0 = 0; __Vi0 < 4; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 5; ++__Vi1) {
            vlSelf->mac_top__DOT__u_array__DOT__h_wire[__Vi0][__Vi1] = VL_RAND_RESET_I(8);
        }
    }
    for (int __Vi0 = 0; __Vi0 < 5; ++__Vi0) {
        for (int __Vi1 = 0; __Vi1 < 4; ++__Vi1) {
            vlSelf->mac_top__DOT__u_array__DOT__v_wire[__Vi0][__Vi1] = VL_RAND_RESET_I(32);
        }
    }
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = VL_RAND_RESET_I(32);
    vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = VL_RAND_RESET_I(8);
    vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = VL_RAND_RESET_I(16);
    vlSelf->__Vtrigprevexpr___TOP__clk__0 = VL_RAND_RESET_I(1);
    vlSelf->__Vtrigprevexpr___TOP__rst_n__0 = VL_RAND_RESET_I(1);
    for (int __Vi0 = 0; __Vi0 < 2; ++__Vi0) {
        vlSelf->__Vm_traceActivity[__Vi0] = 0;
    }
}
