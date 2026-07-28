// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vmac_top.h for the primary calling header

#include "Vmac_top__pch.h"
#include "Vmac_top___024root.h"

VL_INLINE_OPT void Vmac_top___024root___ico_sequent__TOP__0(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___ico_sequent__TOP__0\n"); );
    // Body
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
}

void Vmac_top___024root___eval_ico(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_ico\n"); );
    // Body
    if ((1ULL & vlSelf->__VicoTriggered.word(0U))) {
        Vmac_top___024root___ico_sequent__TOP__0(vlSelf);
    }
}

void Vmac_top___024root___eval_triggers__ico(Vmac_top___024root* vlSelf);

bool Vmac_top___024root___eval_phase__ico(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_phase__ico\n"); );
    // Init
    CData/*0:0*/ __VicoExecute;
    // Body
    Vmac_top___024root___eval_triggers__ico(vlSelf);
    __VicoExecute = vlSelf->__VicoTriggered.any();
    if (__VicoExecute) {
        Vmac_top___024root___eval_ico(vlSelf);
    }
    return (__VicoExecute);
}

void Vmac_top___024root___eval_act(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_act\n"); );
}

VL_INLINE_OPT void Vmac_top___024root___nba_sequent__TOP__0(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___nba_sequent__TOP__0\n"); );
    // Init
    CData/*3:0*/ __Vdly__mac_top__DOT__feed_cnt;
    __Vdly__mac_top__DOT__feed_cnt = 0;
    CData/*3:0*/ __Vdly__mac_top__DOT__drain_cnt;
    __Vdly__mac_top__DOT__drain_cnt = 0;
    IData/*31:0*/ __Vdlyvval__mac_top__DOT__result_hold__v0;
    __Vdlyvval__mac_top__DOT__result_hold__v0 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__result_hold__v0;
    __Vdlyvset__mac_top__DOT__result_hold__v0 = 0;
    IData/*31:0*/ __Vdlyvval__mac_top__DOT__result_hold__v1;
    __Vdlyvval__mac_top__DOT__result_hold__v1 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__result_hold__v1;
    __Vdlyvset__mac_top__DOT__result_hold__v1 = 0;
    IData/*31:0*/ __Vdlyvval__mac_top__DOT__result_hold__v2;
    __Vdlyvval__mac_top__DOT__result_hold__v2 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__result_hold__v2;
    __Vdlyvset__mac_top__DOT__result_hold__v2 = 0;
    IData/*31:0*/ __Vdlyvval__mac_top__DOT__result_hold__v3;
    __Vdlyvval__mac_top__DOT__result_hold__v3 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__result_hold__v3;
    __Vdlyvset__mac_top__DOT__result_hold__v3 = 0;
    CData/*1:0*/ __Vdly__mac_top__DOT__res_cnt;
    __Vdly__mac_top__DOT__res_cnt = 0;
    CData/*1:0*/ __Vdlyvdim0__mac_top__DOT__wgt_buf__v0;
    __Vdlyvdim0__mac_top__DOT__wgt_buf__v0 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__wgt_buf__v0;
    __Vdlyvval__mac_top__DOT__wgt_buf__v0 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__wgt_buf__v0;
    __Vdlyvset__mac_top__DOT__wgt_buf__v0 = 0;
    CData/*1:0*/ __Vdlyvdim0__mac_top__DOT__wgt_buf__v1;
    __Vdlyvdim0__mac_top__DOT__wgt_buf__v1 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__wgt_buf__v1;
    __Vdlyvval__mac_top__DOT__wgt_buf__v1 = 0;
    CData/*1:0*/ __Vdlyvdim0__mac_top__DOT__wgt_buf__v2;
    __Vdlyvdim0__mac_top__DOT__wgt_buf__v2 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__wgt_buf__v2;
    __Vdlyvval__mac_top__DOT__wgt_buf__v2 = 0;
    CData/*1:0*/ __Vdlyvdim0__mac_top__DOT__wgt_buf__v3;
    __Vdlyvdim0__mac_top__DOT__wgt_buf__v3 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__wgt_buf__v3;
    __Vdlyvval__mac_top__DOT__wgt_buf__v3 = 0;
    CData/*1:0*/ __Vdly__mac_top__DOT__wgt_cnt;
    __Vdly__mac_top__DOT__wgt_cnt = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__act_buf__v0;
    __Vdlyvval__mac_top__DOT__act_buf__v0 = 0;
    CData/*0:0*/ __Vdlyvset__mac_top__DOT__act_buf__v0;
    __Vdlyvset__mac_top__DOT__act_buf__v0 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__act_buf__v1;
    __Vdlyvval__mac_top__DOT__act_buf__v1 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__act_buf__v2;
    __Vdlyvval__mac_top__DOT__act_buf__v2 = 0;
    CData/*7:0*/ __Vdlyvval__mac_top__DOT__act_buf__v3;
    __Vdlyvval__mac_top__DOT__act_buf__v3 = 0;
    // Body
    __Vdly__mac_top__DOT__feed_cnt = vlSelf->mac_top__DOT__feed_cnt;
    __Vdly__mac_top__DOT__res_cnt = vlSelf->mac_top__DOT__res_cnt;
    __Vdly__mac_top__DOT__drain_cnt = vlSelf->mac_top__DOT__drain_cnt;
    __Vdlyvset__mac_top__DOT__result_hold__v0 = 0U;
    __Vdlyvset__mac_top__DOT__result_hold__v1 = 0U;
    __Vdlyvset__mac_top__DOT__result_hold__v2 = 0U;
    __Vdlyvset__mac_top__DOT__result_hold__v3 = 0U;
    __Vdlyvset__mac_top__DOT__act_buf__v0 = 0U;
    __Vdly__mac_top__DOT__wgt_cnt = vlSelf->mac_top__DOT__wgt_cnt;
    __Vdlyvset__mac_top__DOT__wgt_buf__v0 = 0U;
    if (vlSelf->rst_n) {
        if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                      >> 3U)))) {
            if ((4U & (IData)(vlSelf->mac_top__DOT__state))) {
                if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
                    if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                        __Vdly__mac_top__DOT__feed_cnt = 0U;
                        vlSelf->mac_top__DOT__row_cnt 
                            = (0xffU & ((IData)(1U) 
                                        + (IData)(vlSelf->mac_top__DOT__row_cnt)));
                        __Vdly__mac_top__DOT__drain_cnt = 0U;
                        __Vdly__mac_top__DOT__res_cnt = 0U;
                        vlSelf->mac_top__DOT__res_done_r = 0U;
                        vlSelf->mac_top__DOT__wgt_done_r = 0U;
                    } else {
                        __Vdly__mac_top__DOT__res_cnt 
                            = (3U & ((IData)(1U) + (IData)(vlSelf->mac_top__DOT__res_cnt)));
                        if ((3U == (IData)(vlSelf->mac_top__DOT__res_cnt))) {
                            vlSelf->mac_top__DOT__res_done_r = 1U;
                        }
                    }
                } else {
                    if ((1U & (~ (IData)(vlSelf->mac_top__DOT__state)))) {
                        __Vdly__mac_top__DOT__feed_cnt 
                            = (0xfU & ((IData)(1U) 
                                       + (IData)(vlSelf->mac_top__DOT__feed_cnt)));
                    }
                    if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                        __Vdly__mac_top__DOT__drain_cnt 
                            = (0xfU & ((IData)(1U) 
                                       + (IData)(vlSelf->mac_top__DOT__drain_cnt)));
                        if ((1U == (IData)(vlSelf->mac_top__DOT__drain_cnt))) {
                            __Vdlyvval__mac_top__DOT__result_hold__v0 
                                = vlSelf->mac_top__DOT__col_out
                                [0U];
                            __Vdlyvset__mac_top__DOT__result_hold__v0 = 1U;
                        }
                        if ((3U == (IData)(vlSelf->mac_top__DOT__drain_cnt))) {
                            __Vdlyvval__mac_top__DOT__result_hold__v1 
                                = vlSelf->mac_top__DOT__col_out
                                [1U];
                            __Vdlyvset__mac_top__DOT__result_hold__v1 = 1U;
                        }
                        if ((5U == (IData)(vlSelf->mac_top__DOT__drain_cnt))) {
                            __Vdlyvval__mac_top__DOT__result_hold__v2 
                                = vlSelf->mac_top__DOT__col_out
                                [2U];
                            __Vdlyvset__mac_top__DOT__result_hold__v2 = 1U;
                        }
                        if ((7U == (IData)(vlSelf->mac_top__DOT__drain_cnt))) {
                            __Vdlyvval__mac_top__DOT__result_hold__v3 
                                = vlSelf->mac_top__DOT__col_out
                                [3U];
                            __Vdlyvset__mac_top__DOT__result_hold__v3 = 1U;
                        }
                    }
                }
            } else if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                                 >> 1U)))) {
                if ((1U & (~ (IData)(vlSelf->mac_top__DOT__state)))) {
                    __Vdly__mac_top__DOT__feed_cnt = 0U;
                    vlSelf->mac_top__DOT__row_cnt = 0U;
                    __Vdly__mac_top__DOT__drain_cnt = 0U;
                    __Vdly__mac_top__DOT__res_cnt = 0U;
                    vlSelf->mac_top__DOT__res_done_r = 0U;
                }
                if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                    if (vlSelf->m_rvalid_i) {
                        __Vdlyvval__mac_top__DOT__wgt_buf__v0 
                            = (0xffU & vlSelf->m_rdata_i);
                        __Vdlyvset__mac_top__DOT__wgt_buf__v0 = 1U;
                        __Vdlyvdim0__mac_top__DOT__wgt_buf__v0 
                            = vlSelf->mac_top__DOT__wgt_cnt;
                        __Vdlyvval__mac_top__DOT__wgt_buf__v1 
                            = (0xffU & (vlSelf->m_rdata_i 
                                        >> 8U));
                        __Vdlyvdim0__mac_top__DOT__wgt_buf__v1 
                            = vlSelf->mac_top__DOT__wgt_cnt;
                        __Vdlyvval__mac_top__DOT__wgt_buf__v2 
                            = (0xffU & (vlSelf->m_rdata_i 
                                        >> 0x10U));
                        __Vdlyvdim0__mac_top__DOT__wgt_buf__v2 
                            = vlSelf->mac_top__DOT__wgt_cnt;
                        __Vdlyvval__mac_top__DOT__wgt_buf__v3 
                            = (vlSelf->m_rdata_i >> 0x18U);
                        __Vdlyvdim0__mac_top__DOT__wgt_buf__v3 
                            = vlSelf->mac_top__DOT__wgt_cnt;
                        __Vdly__mac_top__DOT__wgt_cnt 
                            = (3U & ((IData)(1U) + (IData)(vlSelf->mac_top__DOT__wgt_cnt)));
                        if ((3U == (IData)(vlSelf->mac_top__DOT__wgt_cnt))) {
                            vlSelf->mac_top__DOT__wgt_done_r = 1U;
                        }
                    }
                } else {
                    __Vdly__mac_top__DOT__wgt_cnt = 0U;
                    vlSelf->mac_top__DOT__wgt_done_r = 0U;
                }
            }
            if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                          >> 2U)))) {
                if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
                    if ((1U & (IData)(vlSelf->mac_top__DOT__state))) {
                        if (vlSelf->m_rvalid_i) {
                            __Vdlyvval__mac_top__DOT__act_buf__v0 
                                = (0xffU & vlSelf->m_rdata_i);
                            __Vdlyvset__mac_top__DOT__act_buf__v0 = 1U;
                            __Vdlyvval__mac_top__DOT__act_buf__v1 
                                = (0xffU & (vlSelf->m_rdata_i 
                                            >> 8U));
                            __Vdlyvval__mac_top__DOT__act_buf__v2 
                                = (0xffU & (vlSelf->m_rdata_i 
                                            >> 0x10U));
                            __Vdlyvval__mac_top__DOT__act_buf__v3 
                                = (vlSelf->m_rdata_i 
                                   >> 0x18U);
                        }
                    }
                }
            }
        }
        vlSelf->mac_top__DOT__start = 0U;
        if (vlSelf->done_o) {
            vlSelf->mac_top__DOT__u_regs__DOT__sticky_done = 1U;
        }
        if ((((IData)(vlSelf->psel) & (IData)(vlSelf->penable)) 
             & (IData)(vlSelf->pwrite))) {
            if ((0U == (0xffU & vlSelf->paddr))) {
                vlSelf->mac_top__DOT__start = (1U & vlSelf->pwdata);
            }
            if ((0U != (0xffU & vlSelf->paddr))) {
                if ((8U == (0xffU & vlSelf->paddr))) {
                    vlSelf->mac_top__DOT__reg_k = (0xffU 
                                                   & (vlSelf->pwdata 
                                                      >> 8U));
                    vlSelf->mac_top__DOT__reg_n = (0xffU 
                                                   & vlSelf->pwdata);
                    vlSelf->mac_top__DOT__reg_m = (0xffU 
                                                   & (vlSelf->pwdata 
                                                      >> 0x10U));
                }
                if ((8U != (0xffU & vlSelf->paddr))) {
                    if ((0x18U == (0xffU & vlSelf->paddr))) {
                        vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg 
                            = (0xfU & vlSelf->pwdata);
                    }
                    if ((0x18U != (0xffU & vlSelf->paddr))) {
                        if ((0x20U != (0xffU & vlSelf->paddr))) {
                            if ((0x24U != (0xffU & vlSelf->paddr))) {
                                if ((0x28U == (0xffU 
                                               & vlSelf->paddr))) {
                                    vlSelf->mac_top__DOT__res_addr 
                                        = vlSelf->pwdata;
                                }
                            }
                            if ((0x24U == (0xffU & vlSelf->paddr))) {
                                vlSelf->mac_top__DOT__act_addr 
                                    = vlSelf->pwdata;
                            }
                        }
                        if ((0x20U == (0xffU & vlSelf->paddr))) {
                            vlSelf->mac_top__DOT__wgt_addr 
                                = vlSelf->pwdata;
                        }
                    }
                }
            }
            if (((4U == (0xffU & vlSelf->paddr)) & 
                 (vlSelf->pwdata >> 3U))) {
                vlSelf->mac_top__DOT__u_regs__DOT__sticky_done = 0U;
            }
        }
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [3U][3U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [3U][2U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [3U][1U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [3U][0U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [2U][3U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [2U][2U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [2U][1U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [2U][0U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [1U][3U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [1U][2U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [1U][1U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [1U][0U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [0U][3U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [0U][2U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [0U][1U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out 
            = (vlSelf->mac_top__DOT__u_array__DOT__v_wire
               [0U][0U] + (((- (IData)((1U & ((IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg) 
                                              >> 0xfU)))) 
                            << 0x10U) | (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg)));
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg 
            = (0xffffU & VL_MULS_III(16, (0xffffU & 
                                          VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg))), 
                                     (0xffffU & VL_EXTENDS_II(16,8, (IData)(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg)))));
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out 
            = vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg;
        vlSelf->mac_top__DOT__state = vlSelf->mac_top__DOT__next_state;
        if (vlSelf->mac_top__DOT__load_wgt) {
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [3U][3U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [3U][2U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [3U][1U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [3U][0U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [2U][3U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [2U][2U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [2U][1U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [2U][0U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [1U][3U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [1U][2U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [1U][1U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [1U][0U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [0U][3U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [0U][2U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [0U][1U];
            vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg 
                = vlSelf->mac_top__DOT__u_array__DOT__weight_in
                [0U][0U];
        }
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [3U][3U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [3U][2U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [3U][1U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [3U][0U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [2U][3U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [2U][2U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [2U][1U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [2U][0U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [1U][3U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [1U][2U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [1U][1U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [1U][0U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [0U][3U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [0U][2U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [0U][1U];
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg 
            = vlSelf->mac_top__DOT__u_array__DOT__h_wire
            [0U][0U];
    } else {
        __Vdly__mac_top__DOT__feed_cnt = 0U;
        vlSelf->mac_top__DOT__row_cnt = 0U;
        __Vdly__mac_top__DOT__drain_cnt = 0U;
        vlSelf->mac_top__DOT__start = 0U;
        vlSelf->mac_top__DOT__reg_k = 4U;
        vlSelf->mac_top__DOT__reg_n = 4U;
        vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg = 0U;
        vlSelf->mac_top__DOT__u_regs__DOT__sticky_done = 0U;
        vlSelf->mac_top__DOT__reg_m = 4U;
        vlSelf->mac_top__DOT__res_addr = 0x10000020U;
        vlSelf->mac_top__DOT__act_addr = 0x10000010U;
        vlSelf->mac_top__DOT__wgt_addr = 0x10000000U;
        __Vdly__mac_top__DOT__res_cnt = 0U;
        vlSelf->mac_top__DOT__res_done_r = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out = 0U;
        __Vdly__mac_top__DOT__wgt_cnt = 0U;
        vlSelf->mac_top__DOT__wgt_done_r = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out = 0U;
        vlSelf->mac_top__DOT__state = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg = 0U;
        vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg = 0U;
    }
    vlSelf->mac_top__DOT__feed_cnt = __Vdly__mac_top__DOT__feed_cnt;
    vlSelf->mac_top__DOT__drain_cnt = __Vdly__mac_top__DOT__drain_cnt;
    if (__Vdlyvset__mac_top__DOT__result_hold__v0) {
        vlSelf->mac_top__DOT__result_hold[0U] = __Vdlyvval__mac_top__DOT__result_hold__v0;
    }
    if (__Vdlyvset__mac_top__DOT__result_hold__v1) {
        vlSelf->mac_top__DOT__result_hold[1U] = __Vdlyvval__mac_top__DOT__result_hold__v1;
    }
    if (__Vdlyvset__mac_top__DOT__result_hold__v2) {
        vlSelf->mac_top__DOT__result_hold[2U] = __Vdlyvval__mac_top__DOT__result_hold__v2;
    }
    if (__Vdlyvset__mac_top__DOT__result_hold__v3) {
        vlSelf->mac_top__DOT__result_hold[3U] = __Vdlyvval__mac_top__DOT__result_hold__v3;
    }
    if (__Vdlyvset__mac_top__DOT__act_buf__v0) {
        vlSelf->mac_top__DOT__act_buf[0U] = __Vdlyvval__mac_top__DOT__act_buf__v0;
        vlSelf->mac_top__DOT__act_buf[1U] = __Vdlyvval__mac_top__DOT__act_buf__v1;
        vlSelf->mac_top__DOT__act_buf[2U] = __Vdlyvval__mac_top__DOT__act_buf__v2;
        vlSelf->mac_top__DOT__act_buf[3U] = __Vdlyvval__mac_top__DOT__act_buf__v3;
    }
    vlSelf->mac_top__DOT__res_cnt = __Vdly__mac_top__DOT__res_cnt;
    vlSelf->mac_top__DOT__wgt_cnt = __Vdly__mac_top__DOT__wgt_cnt;
    if (__Vdlyvset__mac_top__DOT__wgt_buf__v0) {
        vlSelf->mac_top__DOT__wgt_buf[__Vdlyvdim0__mac_top__DOT__wgt_buf__v0][0U] 
            = __Vdlyvval__mac_top__DOT__wgt_buf__v0;
        vlSelf->mac_top__DOT__wgt_buf[__Vdlyvdim0__mac_top__DOT__wgt_buf__v1][1U] 
            = __Vdlyvval__mac_top__DOT__wgt_buf__v1;
        vlSelf->mac_top__DOT__wgt_buf[__Vdlyvdim0__mac_top__DOT__wgt_buf__v2][2U] 
            = __Vdlyvval__mac_top__DOT__wgt_buf__v2;
        vlSelf->mac_top__DOT__wgt_buf[__Vdlyvdim0__mac_top__DOT__wgt_buf__v3][3U] 
            = __Vdlyvval__mac_top__DOT__wgt_buf__v3;
    }
    vlSelf->result_hold_o_0 = vlSelf->mac_top__DOT__result_hold
        [0U];
    vlSelf->result_hold_o_1 = vlSelf->mac_top__DOT__result_hold
        [1U];
    vlSelf->result_hold_o_2 = vlSelf->mac_top__DOT__result_hold
        [2U];
    vlSelf->result_hold_o_3 = vlSelf->mac_top__DOT__result_hold
        [3U];
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[4U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[3U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[2U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][3U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][2U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][1U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out;
    vlSelf->mac_top__DOT__u_array__DOT__v_wire[1U][0U] 
        = vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out;
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
    vlSelf->mac_top__DOT__row_in[0U] = 0U;
    vlSelf->mac_top__DOT__row_in[1U] = 0U;
    vlSelf->mac_top__DOT__row_in[2U] = 0U;
    vlSelf->mac_top__DOT__row_in[3U] = 0U;
    vlSelf->mac_top__DOT__load_wgt = 0U;
    if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                  >> 3U)))) {
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
        if ((1U & (~ ((IData)(vlSelf->mac_top__DOT__state) 
                      >> 2U)))) {
            if ((2U & (IData)(vlSelf->mac_top__DOT__state))) {
                if ((1U & (~ (IData)(vlSelf->mac_top__DOT__state)))) {
                    vlSelf->mac_top__DOT__load_wgt = 1U;
                }
            }
        }
    }
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
    vlSelf->mac_top__DOT__u_array__DOT__row_in[0U] 
        = vlSelf->mac_top__DOT__row_in[0U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[1U] 
        = vlSelf->mac_top__DOT__row_in[1U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[2U] 
        = vlSelf->mac_top__DOT__row_in[2U];
    vlSelf->mac_top__DOT__u_array__DOT__row_in[3U] 
        = vlSelf->mac_top__DOT__row_in[3U];
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
}

VL_INLINE_OPT void Vmac_top___024root___nba_sequent__TOP__1(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___nba_sequent__TOP__1\n"); );
    // Body
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

void Vmac_top___024root___eval_nba(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_nba\n"); );
    // Body
    if ((1ULL & vlSelf->__VnbaTriggered.word(0U))) {
        Vmac_top___024root___nba_sequent__TOP__0(vlSelf);
        vlSelf->__Vm_traceActivity[1U] = 1U;
        Vmac_top___024root___nba_sequent__TOP__1(vlSelf);
    }
}

void Vmac_top___024root___eval_triggers__act(Vmac_top___024root* vlSelf);

bool Vmac_top___024root___eval_phase__act(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_phase__act\n"); );
    // Init
    VlTriggerVec<1> __VpreTriggered;
    CData/*0:0*/ __VactExecute;
    // Body
    Vmac_top___024root___eval_triggers__act(vlSelf);
    __VactExecute = vlSelf->__VactTriggered.any();
    if (__VactExecute) {
        __VpreTriggered.andNot(vlSelf->__VactTriggered, vlSelf->__VnbaTriggered);
        vlSelf->__VnbaTriggered.thisOr(vlSelf->__VactTriggered);
        Vmac_top___024root___eval_act(vlSelf);
    }
    return (__VactExecute);
}

bool Vmac_top___024root___eval_phase__nba(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_phase__nba\n"); );
    // Init
    CData/*0:0*/ __VnbaExecute;
    // Body
    __VnbaExecute = vlSelf->__VnbaTriggered.any();
    if (__VnbaExecute) {
        Vmac_top___024root___eval_nba(vlSelf);
        vlSelf->__VnbaTriggered.clear();
    }
    return (__VnbaExecute);
}

#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__ico(Vmac_top___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__nba(Vmac_top___024root* vlSelf);
#endif  // VL_DEBUG
#ifdef VL_DEBUG
VL_ATTR_COLD void Vmac_top___024root___dump_triggers__act(Vmac_top___024root* vlSelf);
#endif  // VL_DEBUG

void Vmac_top___024root___eval(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval\n"); );
    // Init
    IData/*31:0*/ __VicoIterCount;
    CData/*0:0*/ __VicoContinue;
    IData/*31:0*/ __VnbaIterCount;
    CData/*0:0*/ __VnbaContinue;
    // Body
    __VicoIterCount = 0U;
    vlSelf->__VicoFirstIteration = 1U;
    __VicoContinue = 1U;
    while (__VicoContinue) {
        if (VL_UNLIKELY((0x64U < __VicoIterCount))) {
#ifdef VL_DEBUG
            Vmac_top___024root___dump_triggers__ico(vlSelf);
#endif
            VL_FATAL_MT("/home/bolter/mini_mac_soc/rtl/accel/mac_top.v", 1, "", "Input combinational region did not converge.");
        }
        __VicoIterCount = ((IData)(1U) + __VicoIterCount);
        __VicoContinue = 0U;
        if (Vmac_top___024root___eval_phase__ico(vlSelf)) {
            __VicoContinue = 1U;
        }
        vlSelf->__VicoFirstIteration = 0U;
    }
    __VnbaIterCount = 0U;
    __VnbaContinue = 1U;
    while (__VnbaContinue) {
        if (VL_UNLIKELY((0x64U < __VnbaIterCount))) {
#ifdef VL_DEBUG
            Vmac_top___024root___dump_triggers__nba(vlSelf);
#endif
            VL_FATAL_MT("/home/bolter/mini_mac_soc/rtl/accel/mac_top.v", 1, "", "NBA region did not converge.");
        }
        __VnbaIterCount = ((IData)(1U) + __VnbaIterCount);
        __VnbaContinue = 0U;
        vlSelf->__VactIterCount = 0U;
        vlSelf->__VactContinue = 1U;
        while (vlSelf->__VactContinue) {
            if (VL_UNLIKELY((0x64U < vlSelf->__VactIterCount))) {
#ifdef VL_DEBUG
                Vmac_top___024root___dump_triggers__act(vlSelf);
#endif
                VL_FATAL_MT("/home/bolter/mini_mac_soc/rtl/accel/mac_top.v", 1, "", "Active region did not converge.");
            }
            vlSelf->__VactIterCount = ((IData)(1U) 
                                       + vlSelf->__VactIterCount);
            vlSelf->__VactContinue = 0U;
            if (Vmac_top___024root___eval_phase__act(vlSelf)) {
                vlSelf->__VactContinue = 1U;
            }
        }
        if (Vmac_top___024root___eval_phase__nba(vlSelf)) {
            __VnbaContinue = 1U;
        }
    }
}

#ifdef VL_DEBUG
void Vmac_top___024root___eval_debug_assertions(Vmac_top___024root* vlSelf) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root___eval_debug_assertions\n"); );
    // Body
    if (VL_UNLIKELY((vlSelf->clk & 0xfeU))) {
        Verilated::overWidthError("clk");}
    if (VL_UNLIKELY((vlSelf->rst_n & 0xfeU))) {
        Verilated::overWidthError("rst_n");}
    if (VL_UNLIKELY((vlSelf->psel & 0xfeU))) {
        Verilated::overWidthError("psel");}
    if (VL_UNLIKELY((vlSelf->penable & 0xfeU))) {
        Verilated::overWidthError("penable");}
    if (VL_UNLIKELY((vlSelf->pwrite & 0xfeU))) {
        Verilated::overWidthError("pwrite");}
    if (VL_UNLIKELY((vlSelf->m_gnt_i & 0xfeU))) {
        Verilated::overWidthError("m_gnt_i");}
    if (VL_UNLIKELY((vlSelf->m_rvalid_i & 0xfeU))) {
        Verilated::overWidthError("m_rvalid_i");}
}
#endif  // VL_DEBUG
