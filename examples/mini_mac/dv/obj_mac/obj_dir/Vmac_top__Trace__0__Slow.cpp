// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Tracing implementation internals
#include "verilated_vcd_c.h"
#include "Vmac_top__Syms.h"


VL_ATTR_COLD void Vmac_top___024root__trace_init_sub__TOP__0(Vmac_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_init_sub__TOP__0\n"); );
    // Init
    const int c = vlSymsp->__Vm_baseCode;
    // Body
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+301,0,"paddr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+302,0,"psel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+303,0,"penable",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+304,0,"pwrite",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+305,0,"pwdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+306,0,"prdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+307,0,"pready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+308,0,"done_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+309,0,"fsm_state_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBit(c+310,0,"m_req_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+311,0,"m_gnt_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+312,0,"m_addr_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+313,0,"m_we_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+314,0,"m_wdata_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+315,0,"m_rvalid_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+316,0,"m_rdata_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+317,0,"result_hold_o_0",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+318,0,"result_hold_o_1",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+319,0,"result_hold_o_2",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+320,0,"result_hold_o_3",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->pushPrefix("mac_top", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+301,0,"paddr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+302,0,"psel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+303,0,"penable",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+304,0,"pwrite",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+305,0,"pwdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+306,0,"prdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+307,0,"pready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+308,0,"done_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+309,0,"fsm_state_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBit(c+310,0,"m_req_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+311,0,"m_gnt_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+312,0,"m_addr_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+313,0,"m_we_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+314,0,"m_wdata_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+315,0,"m_rvalid_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+316,0,"m_rdata_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+317,0,"result_hold_o_0",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+318,0,"result_hold_o_1",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+319,0,"result_hold_o_2",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+320,0,"result_hold_o_3",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+13,0,"start",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+14,0,"reg_m",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+15,0,"reg_k",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+16,0,"reg_n",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+17,0,"wgt_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+18,0,"act_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+19,0,"res_addr",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->pushPrefix("wgt_buf", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->pushPrefix("[0]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+20,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+21,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+22,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+23,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[1]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+24,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+25,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+26,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+27,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[2]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+28,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+29,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+30,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+31,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[3]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+32,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+33,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+34,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+35,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("weight_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->pushPrefix("[0]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+36,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+37,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+38,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+39,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[1]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+40,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+41,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+42,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+43,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[2]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+44,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+45,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+46,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+47,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[3]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+48,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+49,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+50,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+51,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("act_buf", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+52+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 7,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("res_buf", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+322+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->pushPrefix("row_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+57+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 7,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("col_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+1+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("col_out", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+61+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->declBus(c+326,0,"IDLE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+327,0,"WGT_LOAD",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+328,0,"WGT_PRESENT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+329,0,"ACT_LOAD",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+330,0,"FEED",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+331,0,"DRAIN",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+332,0,"RES_STORE",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+333,0,"ROW_NEXT",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+334,0,"DONE_ST",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+65,0,"state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+321,0,"next_state",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+66,0,"wgt_cnt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+67,0,"res_cnt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 1,0);
    tracep->declBus(c+68,0,"row_cnt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+69,0,"feed_cnt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBus(c+70,0,"drain_cnt",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->declBit(c+71,0,"wgt_done_r",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+72,0,"res_done_r",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->pushPrefix("result_hold", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+73+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->declBit(c+77,0,"m_req_c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+78,0,"m_addr_c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+79,0,"m_we_c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+80,0,"m_wdata_c",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->pushPrefix("u_array", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+81,0,"row_in_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+82,0,"row_in_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+83,0,"row_in_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+84,0,"row_in_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+85,0,"w_in_0_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+86,0,"w_in_0_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+87,0,"w_in_0_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+88,0,"w_in_0_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+89,0,"w_in_1_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+90,0,"w_in_1_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+91,0,"w_in_1_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+92,0,"w_in_1_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+93,0,"w_in_2_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+94,0,"w_in_2_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+95,0,"w_in_2_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+96,0,"w_in_2_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+97,0,"w_in_3_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+98,0,"w_in_3_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+99,0,"w_in_3_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+100,0,"w_in_3_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+5,0,"col_in_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+6,0,"col_in_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+7,0,"col_in_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+8,0,"col_in_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+101,0,"col_out_0",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+102,0,"col_out_1",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+103,0,"col_out_2",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+104,0,"col_out_3",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->pushPrefix("row_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+105+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, true,(i+0), 7,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("weight_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->pushPrefix("[0]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+109,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+110,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+111,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+112,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[1]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+113,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+114,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+115,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+116,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[2]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+117,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+118,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+119,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+120,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[3]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+121,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+122,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+123,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+124,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("col_in", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+9+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("col_out", VerilatedTracePrefixType::ARRAY_UNPACKED);
    for (int i = 0; i < 4; ++i) {
        tracep->declBus(c+125+i*1,0,"",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, true,(i+0), 31,0);
    }
    tracep->popPrefix();
    tracep->pushPrefix("h_wire", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->pushPrefix("[0]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+129,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+130,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+131,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+132,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+133,0,"[4]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[1]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+134,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+135,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+136,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+137,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+138,0,"[4]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[2]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+139,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+140,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+141,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+142,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+143,0,"[4]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->pushPrefix("[3]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+144,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+145,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+146,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+147,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+148,0,"[4]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("v_wire", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->pushPrefix("[0]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+149,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+150,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+151,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+152,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->pushPrefix("[1]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+153,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+154,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+155,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+156,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->pushPrefix("[2]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+157,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+158,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+159,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+160,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->pushPrefix("[3]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+161,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+162,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+163,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+164,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->pushPrefix("[4]", VerilatedTracePrefixType::ARRAY_UNPACKED);
    tracep->declBus(c+165,0,"[0]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+166,0,"[1]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+167,0,"[2]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+168,0,"[3]",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_rows[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("gen_cols[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+335,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+335,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+169,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+170,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+171,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+172,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+173,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+174,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+175,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+176,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+335,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+336,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+177,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+178,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+179,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+180,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+181,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+182,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+183,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+184,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+335,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+337,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+185,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+186,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+187,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+188,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+189,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+190,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+191,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+192,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+335,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+338,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+193,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+194,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+195,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+196,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+197,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+198,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+199,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+200,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_rows[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("gen_cols[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+336,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+335,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+201,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+202,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+203,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+204,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+205,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+206,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+207,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+208,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+336,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+336,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+209,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+210,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+211,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+212,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+213,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+214,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+215,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+216,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+336,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+337,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+217,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+218,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+219,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+220,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+221,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+222,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+223,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+224,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+336,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+338,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+225,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+226,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+227,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+228,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+229,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+230,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+231,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+232,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_rows[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("gen_cols[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+337,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+335,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+233,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+234,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+235,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+236,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+237,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+238,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+239,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+240,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+337,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+336,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+241,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+242,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+243,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+244,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+245,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+246,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+247,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+248,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+337,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+337,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+249,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+250,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+251,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+252,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+253,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+254,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+255,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+256,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+337,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+338,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+257,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+258,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+259,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+260,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+261,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+262,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+263,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+264,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_rows[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("gen_cols[0]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+338,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+335,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+265,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+266,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+267,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+268,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+269,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+270,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+271,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+272,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[1]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+338,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+336,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+273,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+274,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+275,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+276,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+277,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+278,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+279,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+280,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[2]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+338,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+337,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+281,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+282,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+283,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+284,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+285,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+286,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+287,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+288,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("gen_cols[3]", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->pushPrefix("inst_pe", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBus(c+338,0,"ROW",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+338,0,"COL",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::PARAMETER, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+56,0,"load_wgt",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+289,0,"a_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+290,0,"w_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+291,0,"acc_in",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+292,0,"a_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+293,0,"acc_out",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+294,0,"a_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+295,0,"w_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+296,0,"mul_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 15,0);
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->popPrefix();
    tracep->pushPrefix("u_regs", VerilatedTracePrefixType::SCOPE_MODULE);
    tracep->declBit(c+299,0,"clk",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+300,0,"rst_n",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+301,0,"paddr",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+302,0,"psel",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+303,0,"penable",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+304,0,"pwrite",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+305,0,"pwdata",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+306,0,"prdata",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+307,0,"pready",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBit(c+13,0,"start_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+309,0,"fsm_state_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 2,0);
    tracep->declBit(c+308,0,"done_i",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+14,0,"reg_m_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+15,0,"reg_k_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+16,0,"reg_n_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 7,0);
    tracep->declBus(c+17,0,"wgt_addr_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+18,0,"act_addr_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+19,0,"res_addr_o",-1, VerilatedTraceSigDirection::OUTPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+317,0,"result_hold_i_0",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+318,0,"result_hold_i_1",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+319,0,"result_hold_i_2",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBus(c+320,0,"result_hold_i_3",-1, VerilatedTraceSigDirection::INPUT, VerilatedTraceSigKind::WIRE, VerilatedTraceSigType::LOGIC, false,-1, 31,0);
    tracep->declBit(c+297,0,"sticky_done",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1);
    tracep->declBus(c+298,0,"pe_addr_reg",-1, VerilatedTraceSigDirection::NONE, VerilatedTraceSigKind::VAR, VerilatedTraceSigType::LOGIC, false,-1, 3,0);
    tracep->popPrefix();
    tracep->popPrefix();
}

VL_ATTR_COLD void Vmac_top___024root__trace_init_top(Vmac_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_init_top\n"); );
    // Body
    Vmac_top___024root__trace_init_sub__TOP__0(vlSelf, tracep);
}

VL_ATTR_COLD void Vmac_top___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
VL_ATTR_COLD void Vmac_top___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vmac_top___024root__trace_chg_0(void* voidSelf, VerilatedVcd::Buffer* bufp);
void Vmac_top___024root__trace_cleanup(void* voidSelf, VerilatedVcd* /*unused*/);

VL_ATTR_COLD void Vmac_top___024root__trace_register(Vmac_top___024root* vlSelf, VerilatedVcd* tracep) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_register\n"); );
    // Body
    tracep->addConstCb(&Vmac_top___024root__trace_const_0, 0U, vlSelf);
    tracep->addFullCb(&Vmac_top___024root__trace_full_0, 0U, vlSelf);
    tracep->addChgCb(&Vmac_top___024root__trace_chg_0, 0U, vlSelf);
    tracep->addCleanupCb(&Vmac_top___024root__trace_cleanup, vlSelf);
}

VL_ATTR_COLD void Vmac_top___024root__trace_const_0_sub_0(Vmac_top___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vmac_top___024root__trace_const_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_const_0\n"); );
    // Init
    Vmac_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vmac_top___024root*>(voidSelf);
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vmac_top___024root__trace_const_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vmac_top___024root__trace_const_0_sub_0(Vmac_top___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_const_0_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    // Body
    bufp->fullIData(oldp+322,(vlSelf->mac_top__DOT__res_buf[0]),32);
    bufp->fullIData(oldp+323,(vlSelf->mac_top__DOT__res_buf[1]),32);
    bufp->fullIData(oldp+324,(vlSelf->mac_top__DOT__res_buf[2]),32);
    bufp->fullIData(oldp+325,(vlSelf->mac_top__DOT__res_buf[3]),32);
    bufp->fullCData(oldp+326,(0U),4);
    bufp->fullCData(oldp+327,(1U),4);
    bufp->fullCData(oldp+328,(2U),4);
    bufp->fullCData(oldp+329,(3U),4);
    bufp->fullCData(oldp+330,(4U),4);
    bufp->fullCData(oldp+331,(5U),4);
    bufp->fullCData(oldp+332,(6U),4);
    bufp->fullCData(oldp+333,(7U),4);
    bufp->fullCData(oldp+334,(8U),4);
    bufp->fullIData(oldp+335,(0U),32);
    bufp->fullIData(oldp+336,(1U),32);
    bufp->fullIData(oldp+337,(2U),32);
    bufp->fullIData(oldp+338,(3U),32);
}

VL_ATTR_COLD void Vmac_top___024root__trace_full_0_sub_0(Vmac_top___024root* vlSelf, VerilatedVcd::Buffer* bufp);

VL_ATTR_COLD void Vmac_top___024root__trace_full_0(void* voidSelf, VerilatedVcd::Buffer* bufp) {
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_full_0\n"); );
    // Init
    Vmac_top___024root* const __restrict vlSelf VL_ATTR_UNUSED = static_cast<Vmac_top___024root*>(voidSelf);
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    // Body
    Vmac_top___024root__trace_full_0_sub_0((&vlSymsp->TOP), bufp);
}

VL_ATTR_COLD void Vmac_top___024root__trace_full_0_sub_0(Vmac_top___024root* vlSelf, VerilatedVcd::Buffer* bufp) {
    if (false && vlSelf) {}  // Prevent unused
    Vmac_top__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vmac_top___024root__trace_full_0_sub_0\n"); );
    // Init
    uint32_t* const oldp VL_ATTR_UNUSED = bufp->oldp(vlSymsp->__Vm_baseCode);
    // Body
    bufp->fullIData(oldp+1,(vlSelf->mac_top__DOT__col_in[0]),32);
    bufp->fullIData(oldp+2,(vlSelf->mac_top__DOT__col_in[1]),32);
    bufp->fullIData(oldp+3,(vlSelf->mac_top__DOT__col_in[2]),32);
    bufp->fullIData(oldp+4,(vlSelf->mac_top__DOT__col_in[3]),32);
    bufp->fullIData(oldp+5,(vlSelf->mac_top__DOT__col_in
                            [0U]),32);
    bufp->fullIData(oldp+6,(vlSelf->mac_top__DOT__col_in
                            [1U]),32);
    bufp->fullIData(oldp+7,(vlSelf->mac_top__DOT__col_in
                            [2U]),32);
    bufp->fullIData(oldp+8,(vlSelf->mac_top__DOT__col_in
                            [3U]),32);
    bufp->fullIData(oldp+9,(vlSelf->mac_top__DOT__u_array__DOT__col_in[0]),32);
    bufp->fullIData(oldp+10,(vlSelf->mac_top__DOT__u_array__DOT__col_in[1]),32);
    bufp->fullIData(oldp+11,(vlSelf->mac_top__DOT__u_array__DOT__col_in[2]),32);
    bufp->fullIData(oldp+12,(vlSelf->mac_top__DOT__u_array__DOT__col_in[3]),32);
    bufp->fullBit(oldp+13,(vlSelf->mac_top__DOT__start));
    bufp->fullCData(oldp+14,(vlSelf->mac_top__DOT__reg_m),8);
    bufp->fullCData(oldp+15,(vlSelf->mac_top__DOT__reg_k),8);
    bufp->fullCData(oldp+16,(vlSelf->mac_top__DOT__reg_n),8);
    bufp->fullIData(oldp+17,(vlSelf->mac_top__DOT__wgt_addr),32);
    bufp->fullIData(oldp+18,(vlSelf->mac_top__DOT__act_addr),32);
    bufp->fullIData(oldp+19,(vlSelf->mac_top__DOT__res_addr),32);
    bufp->fullCData(oldp+20,(vlSelf->mac_top__DOT__wgt_buf
                             [0U][0U]),8);
    bufp->fullCData(oldp+21,(vlSelf->mac_top__DOT__wgt_buf
                             [0U][1U]),8);
    bufp->fullCData(oldp+22,(vlSelf->mac_top__DOT__wgt_buf
                             [0U][2U]),8);
    bufp->fullCData(oldp+23,(vlSelf->mac_top__DOT__wgt_buf
                             [0U][3U]),8);
    bufp->fullCData(oldp+24,(vlSelf->mac_top__DOT__wgt_buf
                             [1U][0U]),8);
    bufp->fullCData(oldp+25,(vlSelf->mac_top__DOT__wgt_buf
                             [1U][1U]),8);
    bufp->fullCData(oldp+26,(vlSelf->mac_top__DOT__wgt_buf
                             [1U][2U]),8);
    bufp->fullCData(oldp+27,(vlSelf->mac_top__DOT__wgt_buf
                             [1U][3U]),8);
    bufp->fullCData(oldp+28,(vlSelf->mac_top__DOT__wgt_buf
                             [2U][0U]),8);
    bufp->fullCData(oldp+29,(vlSelf->mac_top__DOT__wgt_buf
                             [2U][1U]),8);
    bufp->fullCData(oldp+30,(vlSelf->mac_top__DOT__wgt_buf
                             [2U][2U]),8);
    bufp->fullCData(oldp+31,(vlSelf->mac_top__DOT__wgt_buf
                             [2U][3U]),8);
    bufp->fullCData(oldp+32,(vlSelf->mac_top__DOT__wgt_buf
                             [3U][0U]),8);
    bufp->fullCData(oldp+33,(vlSelf->mac_top__DOT__wgt_buf
                             [3U][1U]),8);
    bufp->fullCData(oldp+34,(vlSelf->mac_top__DOT__wgt_buf
                             [3U][2U]),8);
    bufp->fullCData(oldp+35,(vlSelf->mac_top__DOT__wgt_buf
                             [3U][3U]),8);
    bufp->fullCData(oldp+36,(vlSelf->mac_top__DOT__weight_in
                             [0U][0U]),8);
    bufp->fullCData(oldp+37,(vlSelf->mac_top__DOT__weight_in
                             [0U][1U]),8);
    bufp->fullCData(oldp+38,(vlSelf->mac_top__DOT__weight_in
                             [0U][2U]),8);
    bufp->fullCData(oldp+39,(vlSelf->mac_top__DOT__weight_in
                             [0U][3U]),8);
    bufp->fullCData(oldp+40,(vlSelf->mac_top__DOT__weight_in
                             [1U][0U]),8);
    bufp->fullCData(oldp+41,(vlSelf->mac_top__DOT__weight_in
                             [1U][1U]),8);
    bufp->fullCData(oldp+42,(vlSelf->mac_top__DOT__weight_in
                             [1U][2U]),8);
    bufp->fullCData(oldp+43,(vlSelf->mac_top__DOT__weight_in
                             [1U][3U]),8);
    bufp->fullCData(oldp+44,(vlSelf->mac_top__DOT__weight_in
                             [2U][0U]),8);
    bufp->fullCData(oldp+45,(vlSelf->mac_top__DOT__weight_in
                             [2U][1U]),8);
    bufp->fullCData(oldp+46,(vlSelf->mac_top__DOT__weight_in
                             [2U][2U]),8);
    bufp->fullCData(oldp+47,(vlSelf->mac_top__DOT__weight_in
                             [2U][3U]),8);
    bufp->fullCData(oldp+48,(vlSelf->mac_top__DOT__weight_in
                             [3U][0U]),8);
    bufp->fullCData(oldp+49,(vlSelf->mac_top__DOT__weight_in
                             [3U][1U]),8);
    bufp->fullCData(oldp+50,(vlSelf->mac_top__DOT__weight_in
                             [3U][2U]),8);
    bufp->fullCData(oldp+51,(vlSelf->mac_top__DOT__weight_in
                             [3U][3U]),8);
    bufp->fullCData(oldp+52,(vlSelf->mac_top__DOT__act_buf[0]),8);
    bufp->fullCData(oldp+53,(vlSelf->mac_top__DOT__act_buf[1]),8);
    bufp->fullCData(oldp+54,(vlSelf->mac_top__DOT__act_buf[2]),8);
    bufp->fullCData(oldp+55,(vlSelf->mac_top__DOT__act_buf[3]),8);
    bufp->fullBit(oldp+56,(vlSelf->mac_top__DOT__load_wgt));
    bufp->fullCData(oldp+57,(vlSelf->mac_top__DOT__row_in[0]),8);
    bufp->fullCData(oldp+58,(vlSelf->mac_top__DOT__row_in[1]),8);
    bufp->fullCData(oldp+59,(vlSelf->mac_top__DOT__row_in[2]),8);
    bufp->fullCData(oldp+60,(vlSelf->mac_top__DOT__row_in[3]),8);
    bufp->fullIData(oldp+61,(vlSelf->mac_top__DOT__col_out[0]),32);
    bufp->fullIData(oldp+62,(vlSelf->mac_top__DOT__col_out[1]),32);
    bufp->fullIData(oldp+63,(vlSelf->mac_top__DOT__col_out[2]),32);
    bufp->fullIData(oldp+64,(vlSelf->mac_top__DOT__col_out[3]),32);
    bufp->fullCData(oldp+65,(vlSelf->mac_top__DOT__state),4);
    bufp->fullCData(oldp+66,(vlSelf->mac_top__DOT__wgt_cnt),2);
    bufp->fullCData(oldp+67,(vlSelf->mac_top__DOT__res_cnt),2);
    bufp->fullCData(oldp+68,(vlSelf->mac_top__DOT__row_cnt),8);
    bufp->fullCData(oldp+69,(vlSelf->mac_top__DOT__feed_cnt),4);
    bufp->fullCData(oldp+70,(vlSelf->mac_top__DOT__drain_cnt),4);
    bufp->fullBit(oldp+71,(vlSelf->mac_top__DOT__wgt_done_r));
    bufp->fullBit(oldp+72,(vlSelf->mac_top__DOT__res_done_r));
    bufp->fullIData(oldp+73,(vlSelf->mac_top__DOT__result_hold[0]),32);
    bufp->fullIData(oldp+74,(vlSelf->mac_top__DOT__result_hold[1]),32);
    bufp->fullIData(oldp+75,(vlSelf->mac_top__DOT__result_hold[2]),32);
    bufp->fullIData(oldp+76,(vlSelf->mac_top__DOT__result_hold[3]),32);
    bufp->fullBit(oldp+77,(vlSelf->mac_top__DOT__m_req_c));
    bufp->fullIData(oldp+78,(vlSelf->mac_top__DOT__m_addr_c),32);
    bufp->fullBit(oldp+79,(vlSelf->mac_top__DOT__m_we_c));
    bufp->fullIData(oldp+80,(vlSelf->mac_top__DOT__m_wdata_c),32);
    bufp->fullCData(oldp+81,(vlSelf->mac_top__DOT__row_in
                             [0U]),8);
    bufp->fullCData(oldp+82,(vlSelf->mac_top__DOT__row_in
                             [1U]),8);
    bufp->fullCData(oldp+83,(vlSelf->mac_top__DOT__row_in
                             [2U]),8);
    bufp->fullCData(oldp+84,(vlSelf->mac_top__DOT__row_in
                             [3U]),8);
    bufp->fullCData(oldp+85,(vlSelf->mac_top__DOT__weight_in
                             [0U][0U]),8);
    bufp->fullCData(oldp+86,(vlSelf->mac_top__DOT__weight_in
                             [0U][1U]),8);
    bufp->fullCData(oldp+87,(vlSelf->mac_top__DOT__weight_in
                             [0U][2U]),8);
    bufp->fullCData(oldp+88,(vlSelf->mac_top__DOT__weight_in
                             [0U][3U]),8);
    bufp->fullCData(oldp+89,(vlSelf->mac_top__DOT__weight_in
                             [1U][0U]),8);
    bufp->fullCData(oldp+90,(vlSelf->mac_top__DOT__weight_in
                             [1U][1U]),8);
    bufp->fullCData(oldp+91,(vlSelf->mac_top__DOT__weight_in
                             [1U][2U]),8);
    bufp->fullCData(oldp+92,(vlSelf->mac_top__DOT__weight_in
                             [1U][3U]),8);
    bufp->fullCData(oldp+93,(vlSelf->mac_top__DOT__weight_in
                             [2U][0U]),8);
    bufp->fullCData(oldp+94,(vlSelf->mac_top__DOT__weight_in
                             [2U][1U]),8);
    bufp->fullCData(oldp+95,(vlSelf->mac_top__DOT__weight_in
                             [2U][2U]),8);
    bufp->fullCData(oldp+96,(vlSelf->mac_top__DOT__weight_in
                             [2U][3U]),8);
    bufp->fullCData(oldp+97,(vlSelf->mac_top__DOT__weight_in
                             [3U][0U]),8);
    bufp->fullCData(oldp+98,(vlSelf->mac_top__DOT__weight_in
                             [3U][1U]),8);
    bufp->fullCData(oldp+99,(vlSelf->mac_top__DOT__weight_in
                             [3U][2U]),8);
    bufp->fullCData(oldp+100,(vlSelf->mac_top__DOT__weight_in
                              [3U][3U]),8);
    bufp->fullIData(oldp+101,(vlSelf->mac_top__DOT__u_array__DOT__col_out
                              [0U]),32);
    bufp->fullIData(oldp+102,(vlSelf->mac_top__DOT__u_array__DOT__col_out
                              [1U]),32);
    bufp->fullIData(oldp+103,(vlSelf->mac_top__DOT__u_array__DOT__col_out
                              [2U]),32);
    bufp->fullIData(oldp+104,(vlSelf->mac_top__DOT__u_array__DOT__col_out
                              [3U]),32);
    bufp->fullCData(oldp+105,(vlSelf->mac_top__DOT__u_array__DOT__row_in[0]),8);
    bufp->fullCData(oldp+106,(vlSelf->mac_top__DOT__u_array__DOT__row_in[1]),8);
    bufp->fullCData(oldp+107,(vlSelf->mac_top__DOT__u_array__DOT__row_in[2]),8);
    bufp->fullCData(oldp+108,(vlSelf->mac_top__DOT__u_array__DOT__row_in[3]),8);
    bufp->fullCData(oldp+109,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][0U]),8);
    bufp->fullCData(oldp+110,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][1U]),8);
    bufp->fullCData(oldp+111,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][2U]),8);
    bufp->fullCData(oldp+112,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][3U]),8);
    bufp->fullCData(oldp+113,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][0U]),8);
    bufp->fullCData(oldp+114,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][1U]),8);
    bufp->fullCData(oldp+115,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][2U]),8);
    bufp->fullCData(oldp+116,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][3U]),8);
    bufp->fullCData(oldp+117,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][0U]),8);
    bufp->fullCData(oldp+118,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][1U]),8);
    bufp->fullCData(oldp+119,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][2U]),8);
    bufp->fullCData(oldp+120,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][3U]),8);
    bufp->fullCData(oldp+121,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][0U]),8);
    bufp->fullCData(oldp+122,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][1U]),8);
    bufp->fullCData(oldp+123,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][2U]),8);
    bufp->fullCData(oldp+124,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][3U]),8);
    bufp->fullIData(oldp+125,(vlSelf->mac_top__DOT__u_array__DOT__col_out[0]),32);
    bufp->fullIData(oldp+126,(vlSelf->mac_top__DOT__u_array__DOT__col_out[1]),32);
    bufp->fullIData(oldp+127,(vlSelf->mac_top__DOT__u_array__DOT__col_out[2]),32);
    bufp->fullIData(oldp+128,(vlSelf->mac_top__DOT__u_array__DOT__col_out[3]),32);
    bufp->fullCData(oldp+129,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][0U]),8);
    bufp->fullCData(oldp+130,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][1U]),8);
    bufp->fullCData(oldp+131,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][2U]),8);
    bufp->fullCData(oldp+132,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][3U]),8);
    bufp->fullCData(oldp+133,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][4U]),8);
    bufp->fullCData(oldp+134,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][0U]),8);
    bufp->fullCData(oldp+135,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][1U]),8);
    bufp->fullCData(oldp+136,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][2U]),8);
    bufp->fullCData(oldp+137,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][3U]),8);
    bufp->fullCData(oldp+138,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][4U]),8);
    bufp->fullCData(oldp+139,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][0U]),8);
    bufp->fullCData(oldp+140,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][1U]),8);
    bufp->fullCData(oldp+141,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][2U]),8);
    bufp->fullCData(oldp+142,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][3U]),8);
    bufp->fullCData(oldp+143,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][4U]),8);
    bufp->fullCData(oldp+144,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][0U]),8);
    bufp->fullCData(oldp+145,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][1U]),8);
    bufp->fullCData(oldp+146,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][2U]),8);
    bufp->fullCData(oldp+147,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][3U]),8);
    bufp->fullCData(oldp+148,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][4U]),8);
    bufp->fullIData(oldp+149,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][0U]),32);
    bufp->fullIData(oldp+150,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][1U]),32);
    bufp->fullIData(oldp+151,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][2U]),32);
    bufp->fullIData(oldp+152,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][3U]),32);
    bufp->fullIData(oldp+153,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][0U]),32);
    bufp->fullIData(oldp+154,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][1U]),32);
    bufp->fullIData(oldp+155,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][2U]),32);
    bufp->fullIData(oldp+156,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][3U]),32);
    bufp->fullIData(oldp+157,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][0U]),32);
    bufp->fullIData(oldp+158,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][1U]),32);
    bufp->fullIData(oldp+159,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][2U]),32);
    bufp->fullIData(oldp+160,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][3U]),32);
    bufp->fullIData(oldp+161,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][0U]),32);
    bufp->fullIData(oldp+162,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][1U]),32);
    bufp->fullIData(oldp+163,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][2U]),32);
    bufp->fullIData(oldp+164,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][3U]),32);
    bufp->fullIData(oldp+165,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [4U][0U]),32);
    bufp->fullIData(oldp+166,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [4U][1U]),32);
    bufp->fullIData(oldp+167,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [4U][2U]),32);
    bufp->fullIData(oldp+168,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [4U][3U]),32);
    bufp->fullCData(oldp+169,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][0U]),8);
    bufp->fullCData(oldp+170,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][0U]),8);
    bufp->fullIData(oldp+171,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][0U]),32);
    bufp->fullCData(oldp+172,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+173,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+174,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+175,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+176,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+177,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][1U]),8);
    bufp->fullCData(oldp+178,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][1U]),8);
    bufp->fullIData(oldp+179,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][1U]),32);
    bufp->fullCData(oldp+180,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+181,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+182,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+183,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+184,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+185,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][2U]),8);
    bufp->fullCData(oldp+186,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][2U]),8);
    bufp->fullIData(oldp+187,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][2U]),32);
    bufp->fullCData(oldp+188,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+189,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+190,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+191,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+192,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+193,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [0U][3U]),8);
    bufp->fullCData(oldp+194,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [0U][3U]),8);
    bufp->fullIData(oldp+195,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [0U][3U]),32);
    bufp->fullCData(oldp+196,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+197,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+198,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+199,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+200,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__0__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+201,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][0U]),8);
    bufp->fullCData(oldp+202,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][0U]),8);
    bufp->fullIData(oldp+203,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][0U]),32);
    bufp->fullCData(oldp+204,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+205,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+206,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+207,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+208,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+209,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][1U]),8);
    bufp->fullCData(oldp+210,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][1U]),8);
    bufp->fullIData(oldp+211,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][1U]),32);
    bufp->fullCData(oldp+212,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+213,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+214,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+215,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+216,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+217,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][2U]),8);
    bufp->fullCData(oldp+218,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][2U]),8);
    bufp->fullIData(oldp+219,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][2U]),32);
    bufp->fullCData(oldp+220,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+221,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+222,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+223,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+224,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+225,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [1U][3U]),8);
    bufp->fullCData(oldp+226,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [1U][3U]),8);
    bufp->fullIData(oldp+227,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [1U][3U]),32);
    bufp->fullCData(oldp+228,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+229,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+230,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+231,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+232,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__1__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+233,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][0U]),8);
    bufp->fullCData(oldp+234,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][0U]),8);
    bufp->fullIData(oldp+235,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][0U]),32);
    bufp->fullCData(oldp+236,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+237,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+238,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+239,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+240,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+241,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][1U]),8);
    bufp->fullCData(oldp+242,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][1U]),8);
    bufp->fullIData(oldp+243,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][1U]),32);
    bufp->fullCData(oldp+244,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+245,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+246,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+247,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+248,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+249,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][2U]),8);
    bufp->fullCData(oldp+250,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][2U]),8);
    bufp->fullIData(oldp+251,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][2U]),32);
    bufp->fullCData(oldp+252,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+253,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+254,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+255,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+256,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+257,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [2U][3U]),8);
    bufp->fullCData(oldp+258,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [2U][3U]),8);
    bufp->fullIData(oldp+259,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [2U][3U]),32);
    bufp->fullCData(oldp+260,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+261,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+262,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+263,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+264,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__2__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+265,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][0U]),8);
    bufp->fullCData(oldp+266,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][0U]),8);
    bufp->fullIData(oldp+267,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][0U]),32);
    bufp->fullCData(oldp+268,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+269,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+270,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+271,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+272,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__0__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+273,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][1U]),8);
    bufp->fullCData(oldp+274,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][1U]),8);
    bufp->fullIData(oldp+275,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][1U]),32);
    bufp->fullCData(oldp+276,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+277,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+278,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+279,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+280,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__1__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+281,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][2U]),8);
    bufp->fullCData(oldp+282,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][2U]),8);
    bufp->fullIData(oldp+283,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][2U]),32);
    bufp->fullCData(oldp+284,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+285,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+286,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+287,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+288,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__2__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullCData(oldp+289,(vlSelf->mac_top__DOT__u_array__DOT__h_wire
                              [3U][3U]),8);
    bufp->fullCData(oldp+290,(vlSelf->mac_top__DOT__u_array__DOT__weight_in
                              [3U][3U]),8);
    bufp->fullIData(oldp+291,(vlSelf->mac_top__DOT__u_array__DOT__v_wire
                              [3U][3U]),32);
    bufp->fullCData(oldp+292,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__a_out),8);
    bufp->fullIData(oldp+293,(vlSelf->mac_top__DOT__u_array__DOT____Vcellout__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__acc_out),32);
    bufp->fullCData(oldp+294,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__a_reg),8);
    bufp->fullCData(oldp+295,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__w_reg),8);
    bufp->fullSData(oldp+296,(vlSelf->mac_top__DOT__u_array__DOT__gen_rows__BRA__3__KET____DOT__gen_cols__BRA__3__KET____DOT__inst_pe__DOT__mul_reg),16);
    bufp->fullBit(oldp+297,(vlSelf->mac_top__DOT__u_regs__DOT__sticky_done));
    bufp->fullCData(oldp+298,(vlSelf->mac_top__DOT__u_regs__DOT__pe_addr_reg),4);
    bufp->fullBit(oldp+299,(vlSelf->clk));
    bufp->fullBit(oldp+300,(vlSelf->rst_n));
    bufp->fullIData(oldp+301,(vlSelf->paddr),32);
    bufp->fullBit(oldp+302,(vlSelf->psel));
    bufp->fullBit(oldp+303,(vlSelf->penable));
    bufp->fullBit(oldp+304,(vlSelf->pwrite));
    bufp->fullIData(oldp+305,(vlSelf->pwdata),32);
    bufp->fullIData(oldp+306,(vlSelf->prdata),32);
    bufp->fullBit(oldp+307,(vlSelf->pready));
    bufp->fullBit(oldp+308,(vlSelf->done_o));
    bufp->fullCData(oldp+309,(vlSelf->fsm_state_o),3);
    bufp->fullBit(oldp+310,(vlSelf->m_req_o));
    bufp->fullBit(oldp+311,(vlSelf->m_gnt_i));
    bufp->fullIData(oldp+312,(vlSelf->m_addr_o),32);
    bufp->fullBit(oldp+313,(vlSelf->m_we_o));
    bufp->fullIData(oldp+314,(vlSelf->m_wdata_o),32);
    bufp->fullBit(oldp+315,(vlSelf->m_rvalid_i));
    bufp->fullIData(oldp+316,(vlSelf->m_rdata_i),32);
    bufp->fullIData(oldp+317,(vlSelf->result_hold_o_0),32);
    bufp->fullIData(oldp+318,(vlSelf->result_hold_o_1),32);
    bufp->fullIData(oldp+319,(vlSelf->result_hold_o_2),32);
    bufp->fullIData(oldp+320,(vlSelf->result_hold_o_3),32);
    bufp->fullCData(oldp+321,(vlSelf->mac_top__DOT__next_state),4);
}
