// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vmac_top.h for the primary calling header

#include "Vmac_top__pch.h"
#include "Vmac_top__Syms.h"
#include "Vmac_top___024root.h"

void Vmac_top___024root___ctor_var_reset(Vmac_top___024root* vlSelf);

Vmac_top___024root::Vmac_top___024root(Vmac_top__Syms* symsp, const char* v__name)
    : VerilatedModule{v__name}
    , vlSymsp{symsp}
 {
    // Reset structure values
    Vmac_top___024root___ctor_var_reset(this);
}

void Vmac_top___024root::__Vconfigure(bool first) {
    if (false && first) {}  // Prevent unused
}

Vmac_top___024root::~Vmac_top___024root() {
}
