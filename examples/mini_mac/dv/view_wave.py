#!/usr/bin/env python3
"""VCD waveform viewer - ASCII and HTML output."""

import sys
import os
from vcdvcd import VCDVCD

def get_signal_value(sig, time):
    """Get signal value at a given time by scanning tv pairs."""
    if not sig or not sig.tv:
        return '?'
    last_val = sig.tv[0][1]
    for t, val in sig.tv:
        if t > time:
            break
        last_val = val
    return last_val

def int_from_bin(val_str):
    """Convert binary string to int."""
    if isinstance(val_str, bytes):
        val_str = val_str.decode()
    if val_str in ('x', 'X', 'z', 'Z', '?'):
        return -1
    try:
        return int(val_str, 2)
    except ValueError:
        return -1

def render_ascii(vcd_path):
    vcd = VCDVCD(vcd_path)
    end_time = vcd.endtime

    signals = [
        ('TOP.mac_top.clk', 'clk', 8),
        ('TOP.mac_top.rst_n', 'rst_n', 8),
        ('TOP.mac_top.state[3:0]', 'state', 6),
        ('TOP.mac_top.fsm_state_o[2:0]', 'fsm', 4),
        ('TOP.mac_top.done_o', 'done', 8),
        ('TOP.mac_top.start', 'start', 8),
        ('TOP.mac_top.wgt_done_r', 'wgt_done', 5),
        ('TOP.mac_top.res_done_r', 'res_done', 5),
        ('TOP.mac_top.load_wgt', 'load_wgt', 5),
        ('TOP.mac_top.m_req_o', 'm_req', 7),
        ('TOP.mac_top.m_gnt_i', 'm_gnt', 7),
        ('TOP.mac_top.m_we_o', 'm_we', 7),
        ('TOP.mac_top.m_rvalid_i', 'm_rvalid', 5),
        ('TOP.mac_top.m_addr_o[31:0]', 'm_addr', 0),
        ('TOP.mac_top.m_wdata_o[31:0]', 'm_wdata', 0),
        ('TOP.mac_top.m_rdata_i[31:0]', 'm_rdata', 0),
    ]

    headers = []
    widths = []
    for full_name, label, min_width in signals:
        w = max(len(label), min_width)
        widths.append(w)
        headers.append(label)

    # Print header
    print('Time  ', end='')
    for h, w in zip(headers, widths):
        print(f' {h:>{w}}', end='')
    print()

    # Time steps (each clock edge = 10ps, dump every 2 cycles = 20ps)
    time_step = 20
    max_time = min(end_time, 1740)

    fsm_states = ['IDLE', 'WGT_LOAD', 'WGT_PRES', 'ACT_LOAD', 'FEED', 'DRAIN', 'RES_STORE', 'ROW_NEXT', 'DONE_ST']

    for t in range(0, max_time + 1, time_step):
        if t >= 200:
            # Show every 20ps from 200 onwards
            pass
        print(f'{t:>5} ', end='')
        for full_name, label, min_width in signals:
            sig = vcd[full_name]
            w = widths[signals.index((full_name, label, min_width))]
            if 'addr' in full_name or 'data' in full_name or 'wdata' in full_name or 'rdata' in full_name:
                # Multi-bit: show hex value
                val = get_signal_value(sig, t)
                if val and val not in ('?', 'x', 'X'):
                    int_val = int_from_bin(val)
                    if int_val >= 0:
                        print(f' {int_val:>8x}', end='')
                    else:
                        print(f' {"?":>8}', end='')
                else:
                    print(f' {"?":>8}', end='')
            elif full_name == 'TOP.mac_top.state[3:0]':
                val = get_signal_value(sig, t)
                if val and val not in ('?', 'x', 'X'):
                    try:
                        s = int(val, 2)
                        state_name = fsm_states[s] if s < len(fsm_states) else f'ST{s}'
                        print(f' {state_name:>{w}}', end='')
                    except:
                        print(f' {"?":>{w}}', end='')
                else:
                    print(f' {"?":>{w}}', end='')
            elif full_name == 'TOP.mac_top.fsm_state_o[2:0]':
                val = get_signal_value(sig, t)
                if val and val not in ('?', 'x', 'X'):
                    try:
                        s = int(val, 2)
                        print(f' {s:>{w}}', end='')
                    except:
                        print(f' {"?":>{w}}', end='')
                else:
                    print(f' {"?":>{w}}', end='')
            else:
                # Binary signal
                val = get_signal_value(sig, t)
                c = '#' if val == '1' else ('_' if val == '0' else '?')
                print(f' {c:>{w}}', end='')
        print()

def generate_html(vcd_path, output_path):
    vcd = VCDVCD(vcd_path)
    end_time = vcd.endtime

    signals = [
        ('TOP.mac_top.clk', 'clk'),
        ('TOP.mac_top.rst_n', 'rst_n'),
        ('TOP.mac_top.state[3:0]', 'state'),
        ('TOP.mac_top.fsm_state_o[2:0]', 'fsm'),
        ('TOP.mac_top.done_o', 'done'),
        ('TOP.mac_top.start', 'start'),
        ('TOP.mac_top.wgt_done_r', 'wgt_done'),
        ('TOP.mac_top.res_done_r', 'res_done'),
        ('TOP.mac_top.load_wgt', 'load_wgt'),
        ('TOP.mac_top.m_req_o', 'm_req'),
        ('TOP.mac_top.m_gnt_i', 'm_gnt'),
        ('TOP.mac_top.m_we_o', 'm_we'),
        ('TOP.mac_top.m_rvalid_i', 'm_rvalid'),
    ]

    bus_signals = [
        ('TOP.mac_top.m_addr_o[31:0]', 'm_addr'),
        ('TOP.mac_top.m_wdata_o[31:0]', 'm_wdata'),
        ('TOP.mac_top.m_rdata_i[31:0]', 'm_rdata'),
    ]

    time_step = 5
    max_time = min(end_time, 1740)

    svg_w = max_time // time_step * 10 + 200
    row_h = 30
    label_w = 80

    html = []
    html.append('''<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; margin: 20px; }
  h2 { color: #569cd6; }
  .wave-container { display: flex; align-items: center; margin: 2px 0; }
  .wave-label { width: ''' + str(label_w) + '''px; text-align: right; padding-right: 10px; color: #9cdcfe; font-size: 12px; }
  .wave-bus-label { width: ''' + str(label_w) + '''px; text-align: right; padding-right: 10px; color: #ce9178; font-size: 12px; }
  .wave-svg { flex: 1; }
  .axis-label { fill: #808080; font-family: monospace; font-size: 10px; }
  .wave-1 { fill: #569cd6; stroke: #569cd6; }
  .wave-0 { fill: #808080; stroke: #808080; }
  .bus-val { fill: #ce9178; font-family: monospace; font-size: 9px; }
</style></head><body>
<h2>mini-mac-soc MAC Standalone Waveform</h2>
<p>Time range: 0-''' + str(max_time) + ''' ps</p>
<svg width="''' + str(svg_w) + '''" height="''' + str((len(signals) + len(bus_signals)) * row_h + 30) + '''">
  <line x1="''' + str(label_w + 10) + '''" y1="0" x2="''' + str(label_w + 10) + '''" y2="''' + str((len(signals) + len(bus_signals)) * row_h) + '''" stroke="#333" />
''')

    def get_val_at(sig, time):
        if not sig or not sig.tv:
            return '?'
        last_val = sig.tv[0][1]
        for t, val in sig.tv:
            if t > time:
                break
            last_val = val
        return last_val

    # FSM states mapping
    fsm_states = ['IDLE', 'WGT_LOAD', 'WGT_PRES', 'ACT_LOAD', 'FEED', 'DRAIN', 'RES_STORE', 'ROW_NEXT', 'DONE_ST']

    y = 20
    for full_name, label in signals:
        sig = vcd[full_name]
        x = label_w + 10
        prev_val = get_val_at(sig, 0)
        prev_t = 0

        last_state_label = None
        for t in range(time_step, max_time + time_step, time_step):
            val = get_val_at(sig, t)
            x_start = label_w + 10 + (prev_t // time_step) * 10
            x_end = label_w + 10 + (t // time_step) * 10
            w = x_end - x_start

            if full_name == 'TOP.mac_top.state[3:0]':
                svg_class = 'wave-1'
                # state value
                if val != '?' and val != prev_val:
                    try:
                        s = int(str(val), 2)
                        state_name = fsm_states[s] if s < len(fsm_states) else f'ST{s}'
                        html.append(f'  <text x="{x_start + w//2}" y="{y + 18}" text-anchor="middle" class="bus-val">{state_name}</text>')
                    except:
                        pass
            elif full_name == 'TOP.mac_top.fsm_state_o[2:0]':
                svg_class = 'wave-1'
                if val != '?' and val != prev_val:
                    try:
                        s = int(str(val), 2)
                        html.append(f'  <text x="{x_start + w//2}" y="{y + 18}" text-anchor="middle" class="bus-val">{s}</text>')
                    except:
                        pass
            else:
                c = '#' if str(val) == '1' else ('_' if str(val) == '0' else '?')
                svg_class = 'wave-1' if c == '#' else 'wave-0'

            if prev_t > 0 or prev_val != val:
                pass
            html.append(f'  <rect x="{x_start}" y="{y + 8}" width="{w}" height="{10}" class="{svg_class}" />')
            prev_val = val
            prev_t = t

        # label
        html.append(f'  <text x="{label_w - 5}" y="{y + 18}" text-anchor="end" class="wave-label">{label}</text>')
        y += row_h

    # Bus signals
    for full_name, label in bus_signals:
        sig = vcd[full_name]
        x = label_w + 10
        prev_val = get_val_at(sig, 0)
        prev_t = 0

        html.append(f'  <text x="{label_w + 15}" y="{y + 15}" class="bus-val">{label}</text>')

        for t in range(time_step, max_time + time_step, time_step):
            val = get_val_at(sig, t)
            x_start = label_w + 10 + (prev_t // time_step) * 10
            x_end = label_w + 10 + (t // time_step) * 10
            w = x_end - x_start

            if val != prev_val and val != '?' and str(prev_val) != '?':
                try:
                    int_val = int(str(val), 2)
                    html.append(f'  <text x="{x_start + w//2}" y="{y + 15}" text-anchor="middle" class="bus-val">{hex(int_val)}</text>')
                except:
                    pass
            html.append(f'  <line x1="{x_start}" y1="{y + 8}" x2="{x_end}" y2="{y + 8}" class="wave-1" />')
            prev_val = val
            prev_t = t

        y += row_h

    # Time axis
    y_axis = y
    for t in range(0, max_time + 1, 100):
        x = label_w + 10 + (t // time_step) * 10
        html.append(f'  <text x="{x}" y="{y_axis + 15}" class="axis-label">{t}</text>')
        html.append(f'  <line x1="{x}" y1="{y_axis}" x2="{x}" y2="{y_axis + 5}" stroke="#555" />')

    html.append('</svg></body></html>')

    with open(output_path, 'w') as f:
        f.write('\n'.join(html))
    print(f'Waveform HTML saved to: {output_path}')

if __name__ == '__main__':
    vcd_path = '/home/bolter/mini_mac_soc/dv/obj_mac/mac_waveform.vcd'
    if not os.path.exists(vcd_path):
        vcd_path = '/home/bolter/mini_mac_soc/dv/obj_mac/mac_waveform.vcd'

    print('=== Mini-MaC MAC Standalone Waveform ===')
    print()

    html_out = '/home/bolter/mini_mac_soc/dv/obj_mac/waveform.html'
    generate_html(vcd_path, html_out)

    print()
    print('=== ASCII Signal Dump ===')
    print('(signal values at each time point)')
    render_ascii(vcd_path)
