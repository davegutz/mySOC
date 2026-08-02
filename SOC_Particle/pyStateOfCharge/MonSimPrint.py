# MonSimPrint:  Debug prints for MonSim
# Copyright (C) 2026 Dave Gutz
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# See http://www.fsf.org/licensing/licenses/lgpl.txt for full license text.

"""Python model of what's installed on the Particle Photon.  Includes
a monitor object (MON) and a simulation object (SIM).   The monitor is
the EKF and Coulomb Counter.   The SIM is a battery model, that also has a
Coulomb Counter built in."""

from datetime import datetime, timedelta

# noinspection PyPep8Naming
import Globals as G
from Colors import Colors

count_since_last_header = 0
vv_warning_printed = False
HDR_SPREAD = 10


active_color = Colors.reset


def set_color(color):
    global active_color
    active_color = color
    print(color, end="")


# noinspection PyPep8Naming
def print_pair(val1, val2, total_digits, sig_digits, name, print_name, df=False, end="", color=None, tol=1e-3, rtol=1e-3):
    """
    Prints the numerical values of the first and second arguments or the name argument.

    Args:
        val1: First numerical value.
        val2: Second numerical value.
        total_digits (int): Total number of digits (field width for each formatted number).
        sig_digits (int): Number of significant / decimal digits.
        name (str): Name string to print when print_name is True.
        print_name (bool): If True, prints the fifth argument `name` formatted to total length.
                           If False, prints the formatted numerical values separated by one space.
        diff: Optional argument before end. If not None, exercises difference logic coloring when truthy.
        end (str): Trailing character for print (default "").
        color (str): Optional color to set and remember before printing.
        tol (float): Absolute difference tolerance for monver criteria (default 1e-3).
        rtol (float): Relative difference tolerance for monver criteria (default 1e-3).

    Returns:
        str: The printed string.
    """
    global active_color
    if color is not None:
        set_color(color)

    if val2 is None:
        total_len = total_digits
    else:
        total_len = 2 * total_digits

    if print_name:
        out_str = Colors.reset + f"{name:<{total_len}}"
        if active_color:
            out_str += active_color
    else:
        def _fmt(val):
            if val is None:
                return " " * total_digits
            try:
                return f"{val:<{total_digits}.{sig_digits}f}"
            except (ValueError, TypeError):
                return f"{str(val):<{total_digits}}"

        s1 = _fmt(val1)
        if val2 is None:
            out_str = s1
        else:
            s2 = _fmt(val2)
            out_str = f"{s1}{s2}"
            if df and val1 is not None and val2 is not None:
                is_different = False
                try:
                    v1, v2 = float(val1), float(val2)
                    peak = max(abs(v1), abs(v2))
                    threshold = tol + rtol * peak
                    if abs(v1 - v2) > threshold:
                        is_different = True
                except (ValueError, TypeError):
                    if val1 != val2:
                        is_different = True
                if is_different:
                    out_str = Colors.fg.pink + out_str
                    if active_color:
                        out_str += active_color

    if not end:
        out_str += "    "

    print(out_str, end=end)
    return out_str

# noinspection PyPep8Naming
def prn_soc_debug(OPT, leader="", time=None, i_temp=None, mon=None, sim=None):
    execute = False
    # execute = True
    if not execute:
        return
    else:
        if OPT.request_history == 2:  # soc
            if G.i > 0:
                d_dq = OPT.mon_run.delta_q[G.i] - OPT.mon_run.delta_q[G.i - 1]
            else:
                d_dq = OPT.mon_run.delta_q[G.i + 1] - OPT.mon_run.delta_q[G.i]
            if time is not None:
                print("time {:7.3f}".format(time), end="")
            print(" " * 103 + leader, end="")
            print(
                "{:14.7f}".format(OPT.mon_run.Tb_f[G.i]),
                "{:10.7f}".format(mon.Tb_f),
                "{:14.7f}".format(OPT.mon_run.Tb_f[G.i]),
                "{:10.7f}".format(mon.Tb_f),
                "{:12.4f}".format(d_dq),
                "{:11.4f}".format(mon.d_delta_q),
                "{:12.4f}".format(OPT.mon_run.delta_q[G.i]),
                "{:11.4f}".format(mon.delta_q),
                "{:12.1f}".format(OPT.mon_run.qcrs[G.i]),
                "{:9.1f}".format(mon.q_cap_rated_scaled),
                "{:12.1f}".format(OPT.mon_run.q_capacity[G.i]),
                "{:9.1f}".format(mon.q_capacity),
            )
        elif OPT.request_history == 3:  # soc_s
            if time is not None:
                print("time {:7.3f}".format(time), end="")
            print(" " * 522 + leader, end="")
            print(
                "{:11.8f}".format(OPT.mon_run.soc_s[G.i]),
                "{:9.8f}".format(sim.soc),
                "{:14.8f}".format(OPT.sim_run.Tb_f_s[G.i]),
                "{:11.8f}".format(sim.Tb_f),
                "{:15.6f}".format(OPT.sim_run.d_delta_q_s[G.i]),
                "{:13.6f}".format(sim.d_delta_q),
                "{:15.6f}".format(OPT.sim_run.delta_q_s[G.i]),
                "{:13.6f}".format(sim.delta_q),
                "{:2.0f}".format(sim.reset_temp_past),
            )
        elif OPT.request_history == 4:  # temp
            if time is not None:
                print("time {:7.3f}".format(time), end="")
            print(" " * 75 + leader, end="")
            print(
                "{:14.7f}".format(OPT.mon_run.Tb_hdwe_f[G.i]),
                "{:11.7f}".format(mon.Tb_hdwe_f),
                "{:14.7f}".format(OPT.mon_run.Tb_rap[G.i]),
                "{:11.7f}".format(mon.Tb_rap),
                "{:14.7f}".format(OPT.mon_run.Tb_f[G.i]),
                "{:11.7f}".format(mon.Tb_f),
                "{:14.7f}".format(OPT.mon_run.Tb_f[G.i]),
                "{:11.7f}".format(mon.Tb_f),
                "{:14.7f}".format(OPT.mon_run.Tb_hdwe_f_rate[G.i]),
                "{:11.7f}".format(mon.Tb_hdwe_f_rate),
                "{:14.7f}".format(OPT.mon_run.Tb_f_rate[G.i]),
                "{:11.7f}".format(mon.Tb_f_rate),
                "{:14.7f}".format(OPT.mon_run.Tb_f_rate_rap[G.i]),
                "{:11.7f}".format(mon.Tb_f_rate_rap),
            )


# noinspection PyPep8Naming
def print_hist(OPT, SN, i_temp, i_ekf, t, mon, calc_temp, calc_ekf, sim, df=True):
    hdr = None
    match OPT.run_type:
        case "RunSim":
            match OPT.request_history:
                case 0:
                    hdr = ""
                case 1:  # request_history for ekf
                    hdr = print_ekf_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_ekf, calc_temp, df)
                case 2:  # request_history for soc
                    hdr = print_soc_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                case 3:  # request_history for soc_s
                    hdr = print_soc_s_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                case 4:  # request_history for temp
                    hdr = print_temp_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                case 5:  # request_history for volt all
                    hdr = print_volt_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
                case 6:  # request_history for kf
                    hdr = print_kf_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
                case 7:  # request_history for dyn_m
                    hdr = print_dyn_m_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
                case 8:  # request_history for vb_wrap
                    hdr = print_vb_wrap_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
                case 9:  # request_history for dyn_n
                    hdr = print_dyn_n_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
                case 10:  # request_history for cc_diff
                    hdr = print_cc_diff_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
        case "HistSim":
            match OPT.request_history:
                case 0:
                    hdr = ""
                # case 1:
                #     hdr = print_ekf_HistSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                # case 2:
                #     hdr = print_soc_HistSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                case 3:
                    hdr = print_soc_s_HistSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                # case 4:
                #     hdr = print_temp_HistSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df)
                case 5:
                    hdr = print_volt_HistSim(SN, i_temp, i_ekf, t, mon, calc_temp, calc_ekf, df)
                case 10:
                    hdr = print_cc_diff_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df)
    return hdr


# 7
# noinspection PyPep8Naming,PyUnusedLocal
def print_dyn_m_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "ib_amp_lo") or SN.mon_run.ib_amp_lo is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_dyn_"
                f"m_RunSim  (request_hist_in=7)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(bool(SN.mon_run.reset[G.i]), None, 7, 0, 'reset', h, df)
        print_pair(bool(SN.mon_run.reset_temp[G.i]), None, 10, 0, 'reset_temp', h, df)
        print_pair(bool(SN.mon_run.reset_all_faults[G.i]), None, 16, 0, 'reset_all_faults', h, df)
        print_pair(bool(SN.mon_run.soft_reset[G.i]), None, 15, 0, 'soft_reset', h, df)
        print_pair(bool(SN.mon_run.soft_reset_sim[G.i]), None, 15, 0, 'soft_reset_sim', h, df)
        print_pair(bool(SN.mon_run.init_mon[G.i]), None, 15, 0, 'init_mon', h, df)
        print_pair(bool(SN.mon_run.init_sim[G.i]), None, 15, 0, 'init_sim', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 13, 7, 'vb', h, df)
        print_pair(SN.mon_run.ib_amp_hdwe[G.i], mon.ib_amp_hdwe, 14, 5, 'ibmh', h, df)
        print_pair(SN.mon_run.ib_amp_model[G.i], mon.ib_amp_model, 14, 5, 'ibmm', h, df)
        print_pair(bool(SN.mon_run.ib_amp_lo[G.i]), bool(mon.ib_amp_lo), 7, 0, 'ib_amp_lo', h, df)
        print_pair(bool(SN.mon_run.ib_amp_hi[G.i]), bool(mon.ib_amp_hi), 7, 0, 'ib_amp_hi', h, df)
        print_pair(bool(SN.mon_run.ib_lo_active[G.i]), mon.ib_lo_active, 18, 0, 'ib_lo_active', h, df)
        print_pair(bool(SN.mon_run.disable_amp_fault[G.i]), bool(mon.disable_amp_fault), 7, 0, 'dis_amp_flt', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 11, 4, 'dt', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], mon.ib_amp, 15, 6, 'ib_amp', h, df)
        print_pair(SN.mon_run.ib_dyn_T_m[G.i], mon.LoopIbAmp.ChargeTransfer.dt, 9, 4, 'ib_dyn_T_m', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate_m[G.i], mon.LoopIbAmp.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate_m', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate_m[G.i], mon.LoopIbAmp.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate_m', h, df)
        print_pair(SN.mon_run.ib_dyn_m[G.i], mon.LoopIbAmp.ib_dyn, 21, 5, 'ib_dyn_m', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 11, 5, 'vb', h, df)
        print_pair(SN.mon_run.dv_dyn_m[G.i], mon.LoopIbAmp.dv_dyn, 11, 5, 'dv_dyn_m', h, df)
        print_pair(SN.mon_run.vb_model[G.i], mon.LoopIbAmp.vb, 13, 6, 'vb_m', h, df)
        print_pair(SN.mon_run.voc_m[G.i], mon.LoopIbAmp.voc, 13, 6, 'voc_m', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 13, 6, 'voc_soc', h, df)
        print_pair(SN.mon_run.voc_soc_m[G.i], mon.LoopIbAmp.voc_soc, 11, 6, 'voc_soc_m', h, df)
        print_pair(SN.mon_run.e_wrap_m[G.i], mon.e_wrap_m, 13, 5, 'e_wrap_m', h, df)
        print_pair(SN.mon_run.e_wrap_m_trim[G.i], mon.e_wrap_m_trim, 16, 5, 'e_wrap_m_trim', h, df)
        print_pair(SN.mon_run.e_wrap_m_trimmed[G.i], mon.LoopIbAmp.e_wrap_trimmed, 12, 6, 'e_wrap_trimmed_m', h, df)
        print_pair(SN.mon_run.ib_wrp_T_m[G.i], mon.LoopIbAmp.WrapErrFilt.dt, 12, 4, 'e_wrap_m_T', h, df)
        print_pair(SN.mon_run.ib_wrp_rate_m[G.i], mon.LoopIbAmp.WrapErrFilt.rate, 12, 6, 'e_wrap_m_rate', h, df)
        print_pair(bool(SN.mon_run.ib_wrp_reset_m[G.i]), bool(mon.LoopIbAmp.WrapErrFilt.reset), 12, 0, 'e_wrap_m_reset', h, df)
        print_pair(SN.mon_run.ib_wrp_state_m[G.i], mon.LoopIbAmp.WrapErrFilt.state, 12, 6, 'e_wrap_m_state', h, df)
        print_pair(SN.mon_run.e_wrap_m_filt[G.i], mon.e_wrap_m_filt, 11, 5, 'e_wrap_m_filt', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 13, 6, 'voc_soc', h, df)
        print_pair(SN.mon_run.voc_stat[G.i], mon.voc_stat, 11, 5, 'voc_stat', h, df)
        print_pair(SN.mon_run.vsat[G.i], mon.vsat, 11, 5, 'vsat', h, df)
        print_pair(SN.mon_run.ib[G.i], mon.ib, 14, 5, 'ib', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 13, 8, 'soc', h, df)
        print_pair(SN.mon_run.ewmhi_thr[G.i], mon.ewmhi_thr, 11, 5, 'ewmhi_thr', h, df)
        print_pair(SN.mon_run.ewmlo_thr[G.i], mon.ewmlo_thr, 11, 5, 'ewmlo_thr', h, df)
        print_pair(SN.mon_run.wrap_hi_m_flt[G.i], mon.wrap_hi_m_flt, 8, 0, 'e_wrap_m_flt', h, df)
        print_pair(SN.mon_run.wrap_hi_m_fa[G.i], mon.wrap_hi_m_fa, 8, 0, 'e_wrap_m_fa', h, df)
        print_pair(SN.mon_run.disable_amp_fault[G.i], mon.disable_amp_fault, 15, 0, 'disable_amp_fault', h, df)
        print_pair(mon.ib_amp_lo, None, 9, 0, 'ib_amp_lo', h, df)
        print_pair(SN.mon_run.e_wrap_m_reset[G.i], mon.e_wrap_m_reset, 16, 0, 'e_wrap_m_reset', h, df)
        print_pair(SN.mon_run.fltw[G.i], None, 18, 0, 'fltw', h, df)
        print_pair(SN.mon_run.falw[G.i], None, 4, 0, 'falw', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 9
# noinspection PyPep8Naming,PyUnusedLocal
def print_dyn_n_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "ib_noa_lo") or SN.mon_run.ib_noa_lo is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_dyn_"
                f"n_RunSim  (request_hist_in=7)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(bool(SN.mon_run.reset[G.i]), None, 7, 0, 'reset', h, df)
        print_pair(bool(SN.mon_run.reset_temp[G.i]), None, 10, 0, 'reset_temp', h, df)
        print_pair(bool(SN.mon_run.reset_all_faults[G.i]), None, 16, 0, 'reset_all_faults', h, df)
        print_pair(bool(SN.mon_run.soft_reset[G.i]), None, 15, 0, 'soft_reset', h, df)
        print_pair(bool(SN.mon_run.soft_reset_sim[G.i]), None, 15, 0, 'soft_reset_sim', h, df)
        print_pair(bool(SN.mon_run.init_mon[G.i]), None, 15, 0, 'init_mon', h, df)
        print_pair(bool(SN.mon_run.init_sim[G.i]), None, 15, 0, 'init_sim', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 14, 7, 'vb', h, df)
        print_pair(SN.mon_run.ib_noa_hdwe[G.i], mon.ib_noa_hdwe, 15, 5, 'ibmh', h, df)
        print_pair(SN.mon_run.ib_noa_model[G.i], mon.ib_noa_model, 15, 5, 'ibmm', h, df)
        print_pair(bool(SN.mon_run.ib_noa_lo[G.i]), bool(mon.ib_noa_lo), 9, 0, 'ib_noa_lo', h, df)
        print_pair(bool(SN.mon_run.ib_noa_hi[G.i]), bool(mon.ib_noa_hi), 7, 0, 'ib_noa_hi', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 11, 4, 'dt', h, df)
        print_pair(SN.mon_run.ib_noa[G.i], mon.ib_noa, 15, 6, 'ib_noa', h, df)
        print_pair(SN.mon_run.ib_dyn_T_n[G.i], mon.LoopIbNoa.ChargeTransfer.dt, 9, 4, 'ib_dyn_T_n', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate_n[G.i], mon.LoopIbNoa.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate_n', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate_n[G.i], mon.LoopIbNoa.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate_n', h, df)
        print_pair(SN.mon_run.ib_dyn_n[G.i], mon.LoopIbNoa.ib_dyn, 21, 5, 'ib_dyn_n', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 12, 5, 'vb', h, df)
        print_pair(SN.mon_run.dv_dyn_n[G.i], mon.LoopIbNoa.dv_dyn, 12, 5, 'dv_dyn_n', h, df)
        print_pair(SN.mon_run.vb_model[G.i], mon.LoopIbNoa.vb, 13, 6, 'vb_n', h, df)
        print_pair(SN.mon_run.voc_n[G.i], mon.LoopIbNoa.voc, 13, 6, 'voc_n', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 13, 6, 'voc_soc', h, df)
        print_pair(SN.mon_run.voc_soc_n[G.i], mon.LoopIbNoa.voc_soc, 12, 6, 'voc_soc_n', h, df)
        print_pair(SN.mon_run.e_wrap_n[G.i], mon.e_wrap_n, 13, 5, 'e_wrap_n', h, df)
        print_pair(SN.mon_run.e_wrap_n_trim[G.i], mon.e_wrap_n_trim, 16, 5, 'e_wrap_n_trim', h, df)
        print_pair(SN.mon_run.e_wrap_n_trimmed[G.i], mon.LoopIbNoa.e_wrap_trimmed, 12, 6, 'e_wrap_trimmed_n', h, df)
        print_pair(SN.mon_run.ib_wrp_T_n[G.i], mon.LoopIbNoa.WrapErrFilt.dt, 12, 4, 'e_wrap_n_T', h, df)
        print_pair(SN.mon_run.ib_wrp_rate_n[G.i], mon.LoopIbNoa.WrapErrFilt.rate, 12, 6, 'e_wrap_n_rate', h, df)
        print_pair(bool(SN.mon_run.ib_wrp_reset_n[G.i]), bool(mon.LoopIbNoa.WrapErrFilt.reset), 12, 0, 'e_wrap_n_reset', h, df)
        print_pair(SN.mon_run.ib_wrp_state_n[G.i], mon.LoopIbNoa.WrapErrFilt.state, 12, 6, 'e_wrap_n_state', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 12, 5, 'e_wrap_n_filt', h, df)
        print_pair(SN.mon_run.ewmhi_thr[G.i], mon.ewmhi_thr, 12, 5, 'ewmhi_thr', h, df)
        print_pair(SN.mon_run.ewmlo_thr[G.i], mon.ewmlo_thr, 12, 5, 'ewmlo_thr', h, df)
        print_pair(SN.mon_run.wrap_hi_n_flt[G.i], mon.wrap_hi_n_flt, 8, 0, 'e_wrap_n_flt', h, df)
        print_pair(SN.mon_run.wrap_hi_n_fa[G.i], mon.wrap_hi_n_fa, 8, 0, 'e_wrap_n_fa', h, df)
        print_pair(bool(SN.mon_run.ib_noa_lo[G.i]), None, 9, 0, 'ib_noa_lo', h, df)
        print_pair(SN.mon_run.fltw[G.i], None, 18, 0, 'fltw', h, df)
        print_pair(SN.mon_run.falw[G.i], None, 4, 0, 'falw', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 11, 5, 'e_wrap_n_filt', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 1
# noinspection PyPep8Naming,PyUnusedLocal
def print_ekf_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_ekf, calc_temp, df=False):
    global count_since_last_header, vv_warning_printed
    if (not hasattr(SN.mon_run, "voltage_low") or SN.mon_run.voltage_low is None) or (
        not hasattr(SN.mon_run, "frz") or SN.mon_run.frz is None
    ):
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_ekf_"
                f"RunSim  (request_hist_in=1)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    i_ekf = max(i_ekf, 0)
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD or i_ekf == 0
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset_ekf:
        set_color(Colors.fg.red)
    elif mon.u_ekf == 0.0:
        set_color(Colors.fg.yellow)
    elif calc_ekf:
        set_color(Colors.fg.green)
    elif mon.reset_ekf:
        set_color(Colors.fg.lightblue)
    elif mon.reset:
        set_color(Colors.fg.red)
    if not calc_ekf:
        print(Colors.reset, end="")
        return

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 7, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 3, 0, 'r_t', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 6, 3, 'dt', h, df)
        print_pair(SN.sim_run.dt_fut_s[G.i], sim.dt_fut, 6, 3, 'dt_s', h, df)
        print_pair(i_ekf, None, 5, 0, 'i_ekf', h, df)
        print_pair(mon.reset_ekf, None, 9, 0, 'reset_ekf', h, df)
        print_pair(calc_ekf, None, 8, 0, 'calc_ekf', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sat', h, df)
        print_pair(SN.mon_run.voc_stat[G.i], mon.voc_stat, 11, 5, 'voc_stat', h, df)
        print_pair(SN.mon_run.voc_stat[G.i - 1], mon.voc_stat_past, 11, 5, '', h, df)
        print_pair(bool(SN.mon_run.bms_off[G.i - 1]), bool(mon.bms_off_past), 7, 0, 'bms_off_past', h, df)
        print_pair(bool(SN.mon_run.voltage_low[G.i]), bool(mon.voltage_low), 7, 0, 'voltage_low', h, df)
        print_pair(bool(SN.mon_run.bms_off[G.i]), bool(mon.bms_off), 7, 0, 'bms_off', h, df)
        print_pair(SN.mon_run.frz[i_ekf], mon.frz, 7, 0, 'frz', h, df)
        print_pair(SN.mon_run.ib_charge[G.i], mon.ib_charge, 13, 6, 'ib_charge', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 13, 8, 'soc', h, df)
        print_pair(SN.sim_run.ib_in_s[G.i], sim.ib_in_s, 13, 6, 'ib_in_s', h, df)
        print_pair(SN.mon_run.soc_s[G.i], mon.soc_s, 13, 8, 'soc_s', h, df)
        print_pair(SN.mon_run.soc_ekf[G.i], mon.soc_ekf, 11, 8, 'soc_ekf', h, df)
        print_pair(mon.x, None, 12, 8, 'mon.x', h, df)
        print_pair(SN.mon_run.y_ekf[G.i], mon.y_ekf, 12, 8, 'y_ekf', h, df)
        print_pair(SN.mon_run.y_ekf_f[G.i], mon.y_ekf_f, 12, 8, 'y_ekf_f', h, df)
        print_pair(SN.mon_run.y_ekf_f_T[i_ekf], mon.y_ekf_f_T, 12, 8, 'y_ekf_f_T', h, df)
        print_pair(SN.mon_run.y_ekf_f_tau[i_ekf], mon.y_ekf_f_tau, 12, 8, 'y_ekf_f_tau', h, df)
        print_pair(SN.mon_run.y_ekf_f_lstate[i_ekf], mon.y_ekf_f_state, 12, 9, 'y_ekf_f_state', h, df)
        print_pair(SN.mon_run.z[i_ekf], mon.z, 13, 9, 'z', h, df)
        print_pair(SN.mon_run.hx[i_ekf], mon.hx, 15, 9, 'hx', h, df)
        print_pair(SN.mon_run.voc_ekf[G.i], mon.voc_ekf, 13, 9, 'mon.voc_ekf', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 12, 8, 'Tb_f', h, df)
        print_pair(SN.mon_run.x_prior[i_ekf], mon.x_prior, 12, 8, 'x_prior', h, df)
        print_pair(SN.mon_run.x[i_ekf], mon.x, 13, 8, 'x', h, df)
        print_pair(SN.mon_run.x_for_hx[i_ekf], mon.x_for_hx, 15, 10, 'x_for_hx', h, df)
        print_pair(SN.mon_run.x_post[i_ekf], mon.x_post, 13, 8, 'x_post', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.tb_f_for_hx[i_ekf], mon.tb_f_for_hx, 14, 7, 'tb_f_for_hx', h, df)
        print_pair(SN.mon_run.hx[i_ekf], mon.hx, 14, 6, 'hx', h, df)
        print_pair(SN.mon_run.u[i_ekf], mon.u_ekf, 12, 6, 'u_ekf', h, df)
        print_pair(SN.mon_run.voc_stat_f[i_ekf], mon.voc_stat_f, 16, 12, 'voc_stat_f', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 13, 6, 'voc_soc', h, df)
        print_pair(SN.mon_run.z[i_ekf], mon.z, 15, 9, 'z', h, df)
        print_pair(SN.mon_run.P[i_ekf], mon.P, 14, 11, 'P', h, df)
        print_pair(SN.mon_run.P_post[i_ekf], mon.P_post, 14, 11, 'P_post', h, df)
        print_pair(SN.mon_run.P_prior[i_ekf], mon.P_prior, 14, 11, 'P_prior', h, df)
        print_pair(SN.mon_run.Fx[i_ekf], mon.Fx, 13, 9, 'Fx', h, df)
        print_pair(SN.mon_run.Bu[i_ekf], mon.Bu, 15, 12, 'Bu', h, df)
        print_pair(SN.mon_run.H[i_ekf], mon.H, 14, 7, 'H', h, df)
        print_pair(SN.mon_run.H_pst[i_ekf], mon.H_pst, 14, 7, 'H_pst', h, df)
        print_pair(SN.mon_run.R[i_ekf], mon.R, 12, 6, 'R', h, df)
        print_pair(SN.mon_run.S[i_ekf], mon.S, 11, 6, 'S', h, df)
        print_pair(SN.mon_run.K[i_ekf], mon.K, 13, 9, 'K', h, df)
        print_pair(SN.mon_run.Q[i_ekf], mon.Q, 13, 9, 'Q', h, df)
        print_pair(SN.mon_run.R[i_ekf], mon.R, 13, 9, 'R', h, df)
        print_pair(SN.mon_run.voc_stat[G.i], mon.voc_stat, 16, 9, 'voc_stat', h, df=df)
        print_pair(SN.mon_run.voc_stat_f_rstate[i_ekf], mon.voc_stat_f_rstate, 16, 9, 'voc_stat_f_rstate', h, df=df)
        print_pair(SN.mon_run.voc_stat_f_lstate[i_ekf], mon.voc_stat_f_lstate, 16, 9, 'voc_stat_f_lstate', h, df)
        print_pair(SN.mon_run.voc_stat_f_T[i_ekf], mon.voc_stat_f_T, 16, 9, 'voc_stat_f_T', h, df)
        print_pair(SN.mon_run.voc_stat_f[i_ekf], mon.voc_stat_f, 16, 9, 'voc_stat_f', h, df, end="\n")
    print(Colors.reset, end="")
    return 'header'


# 6
# noinspection PyPep8Naming,PyUnusedLocal
def print_kf_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "dtm"):
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1 or vv3-vv4 run.  Not printing pri"
                f"nt_kf_RunSim  (request_hist_in=6)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(SN.mon_run.dtm[G.i], SN.KfShuntAmp.dt, 9, 4, 'dtm', h, df)
        print_pair(SN.mon_run.dtn[G.i], SN.KfShuntNoa.dt, 9, 4, 'dtn', h, df)
        print_pair(SN.mon_run.vovcn[G.i], SN.VoVcn, 12, 7, 'VoVcn', h, df)
        print_pair(SN.mon_run.vovcnkf[G.i], SN.VoVcn_f, 11, 6, 'VoVcnf', h, df)
        print_pair(SN.mon_run.x0n[G.i], SN.KfShuntNoa.x[0][0], 11, 6, 'x0', h, df)
        print_pair(SN.mon_run.iscn[G.i], SN.iscn, 11, 6, 'ib_shunt_noa', h, df)
        print_pair(SN.mon_run.Fx00n[G.i], SN.KfShuntNoa.Fx[0][0], 8, 1, 'Fx00n', h, df)
        print_pair(SN.mon_run.Fx01n[G.i], SN.KfShuntNoa.Fx[0][1], 7, 3, 'Fx01n', h, df)
        print_pair(SN.mon_run.Fx10n[G.i], SN.KfShuntNoa.Fx[1][0], 5, 1, 'Fx10n', h, df)
        print_pair(SN.mon_run.Fx11n[G.i], SN.KfShuntNoa.Fx[1][1], 5, 1, 'Fx11n', h, df)
        print_pair(SN.mon_run.Q00n[G.i], SN.KfShuntNoa.Q[0][0], 18, 7, 'Q00n', h, df)
        print_pair(SN.mon_run.Q01n[G.i], SN.KfShuntNoa.Q[0][1], 14, 7, 'Q01n', h, df)
        print_pair(SN.mon_run.Q10n[G.i], SN.KfShuntNoa.Q[1][0], 14, 7, 'Q10n', h, df)
        print_pair(SN.mon_run.Q11n[G.i], SN.KfShuntNoa.Q[1][1], 14, 7, 'Q11n', h, df)
        print_pair(SN.mon_run.xp0n[G.i], float(SN.KfShuntNoa.x_prior[0, 0]), 11, 6, 'xp0n', h, df)
        print_pair(SN.mon_run.xp1n[G.i], float(SN.KfShuntNoa.x_prior[1, 0]), 11, 6, 'xp1n', h, df)
        print_pair(SN.mon_run.Pp00n[G.i], SN.KfShuntNoa.P_prior[0, 0], 18, 7, 'Pp00n', h, df)
        print_pair(SN.mon_run.Pp01n[G.i], SN.KfShuntNoa.P_prior[0, 1], 14, 7, 'Pp01n', h, df)
        print_pair(SN.mon_run.Pp10n[G.i], SN.KfShuntNoa.P_prior[1, 0], 14, 7, 'Pp10n', h, df)
        print_pair(SN.mon_run.Pp11n[G.i], SN.KfShuntNoa.P_prior[1, 1], 14, 7, 'Pp11n', h, df)
        print_pair(SN.mon_run.Sn[G.i], SN.KfShuntNoa.S, 13, 8, 'S', h, df)
        print_pair(SN.mon_run.K0n[G.i], SN.KfShuntNoa.K[0, 0], 18, 7, 'K0n', h, df)
        print_pair(SN.mon_run.K1n[G.i], SN.KfShuntNoa.K[1, 0], 18, 7, 'K1n', h, df)
        print_pair(SN.mon_run.yn[G.i], SN.KfShuntNoa.y_kf, 11, 6, 'y', h, df)
        print_pair(SN.mon_run.x0n[G.i], SN.KfShuntNoa.x[0][0], 11, 6, 'x0', h, df)
        print_pair(SN.mon_run.kf_v_n[G.i], SN.KfShuntNoa.x[1][0], 11, 6, 'kf_v_n', h, df)
        print_pair(SN.mon_run.P00n[G.i], SN.KfShuntNoa.P[0][0], 18, 7, 'P00n', h, df)
        print_pair(SN.mon_run.P01n[G.i], SN.KfShuntNoa.P[0][1], 14, 7, 'P01n', h, df)
        print_pair(SN.mon_run.P10n[G.i], SN.KfShuntNoa.P[1][0], 14, 7, 'P10n', h, df)
        print_pair(SN.mon_run.P11n[G.i], SN.KfShuntNoa.P[1][1], 14, 7, 'P11n', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'

# 2
# noinspection PyPep8Naming,PyUnusedLocal
def print_soc_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df=False):
    global count_since_last_header
    print_hdr = calc_temp and count_since_last_header > HDR_SPREAD
    if calc_temp and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        d_dq = SN.mon_run.delta_q[G.i] - SN.mon_run.delta_q[G.i - 1]
        count_since_last_header += 1
    else:
        d_dq = SN.mon_run.delta_q[G.i + 1] - SN.mon_run.delta_q[G.i]
    i_dt_old = SN.mon_run.dt[G.i] * SN.mon_run.ib_charge[G.i]
    i_dt_new = mon.dt * mon.ib_charge
    if mon.ib_charge > 0:
        i_dt_old *= mon.chemistry.coul_eff
        i_dt_new *= mon.chemistry.coul_eff
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 7, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.mon_run.ib_charge[G.i], mon.ib_charge, 12, 4, 'ib_charge', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 11, 7, 'soc', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(i_dt_old, i_dt_new, 12, 4, 'i * dt * coul_eff', h, df)
        print_pair(SN.mon_run.d_delta_q[G.i], mon.d_delta_q, 15, 7, 'd_delq', h, df)
        print_pair(SN.mon_run.delta_q[G.i], mon.delta_q, 16, 3, 'delq', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(d_dq, mon.d_delta_q, 12, 3, 'ddq', h, df)
        print_pair(SN.mon_run.delta_q[G.i], mon.delta_q, 16, 2, 'delq', h, df)
        print_pair(SN.mon_run.qcrs[G.i], mon.q_cap_rated_scaled, 15, 2, 'qcrs', h, df)
        print_pair(SN.mon_run.q_capacity[G.i], mon.q_capacity, 15, 2, 'q_capacity', h, df)
        print_pair(SN.mon_run.Tb[G.i], mon.Tb, 14, 7, 'Tb', h, df)
        print_pair(SN.mon_run.Tb_f_rate[G.i], mon.Tb_f_rate, 12, 7, 'Tb_f_rate', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 3
# noinspection PyPep8Naming
def print_soc_s_HistSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df=False):
    global count_since_last_header
    print_hdr = calc_temp and count_since_last_header > HDR_SPREAD
    if calc_temp and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 7, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.sim_run.sat_s[G.i], sim.sat, 5, 0, 'sa_s', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 12, 4, 'dt', h, df)
        print_pair(SN.sim_run.dt_s[G.i], sim.dt, 12, 4, 'dt_s', h, df)
        print_pair(SN.sim_run.ib_in_s[G.i], sim.ib_in, 14, 5, 'ib_in_s', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 14, 5, 'ib_dyn', h, df)
        print_pair(SN.sim_run.dv_hys_s[G.i], sim.dv_hys, 12, 5, 'dv_hys_s', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 11, 7, 'soc', h, df)
        print_pair(SN.mon_run.delta_q[G.i], mon.delta_q, 16, 6, 'delq', h, df)
        print_pair(SN.mon_run.soc_s[G.i], sim.soc, 11, 6, 'soc_s', h, df)
        print_pair(SN.sim_run.delta_q_s[G.i], sim.delta_q, 15, 6, 'delta_q_s', h, df)
        print_pair(SN.mon_run.qcrs[G.i], mon.q_cap_rated_scaled, 12, 2, 'qcrs', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.vb_f[G.i], mon.vb, 11, 5, 'vb', h, df)
        print_pair(SN.mon_run.voc_stat_f[G.i], mon.voc_stat, 11, 5, 'voc_stat', h, df)
        print_pair(SN.sim_run.voc_stat_s[G.i], sim.voc_stat, 11, 5, 'voc_stat_s', h, df)
        print_pair(SN.sim_run.dv_hys_s[G.i], sim.dv_hys, 11, 5, 'dv_hys_s', h, df)
        print_pair(SN.sim_run.dv_dyn_s[G.i], sim.dv_dyn, 11, 5, 'dv_dyn_s', h, df)
        print_pair(SN.mon_run.vsat[G.i], mon.vsat, 11, 5, 'vsat', h, df)
        print_pair(bool(SN.sim_run.bms_off_s[G.i]), sim.bms_off, 7, 0, 'bms_off_s', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 3
# noinspection PyPep8Naming
def print_soc_s_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.sim_run, "ib_charge_s") or SN.sim_run.ib_charge_s is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_soc_"
                f"s_RunSim (request_hist_in=3)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = calc_temp and count_since_last_header > HDR_SPREAD
    if calc_temp and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    i_dt_old = SN.mon_run.dt[G.i] * SN.mon_run.ib_charge[G.i]
    i_dt_new = mon.dt * mon.ib_charge
    if mon.ib_charge > 0:
        i_dt_old *= mon.chemistry.coul_eff
        i_dt_new *= mon.chemistry.coul_eff
    i_dt_old_s = SN.sim_run.dt_charge_s[G.i] * SN.sim_run.ib_charge_s[G.i]
    i_dt_new_s = sim.dt_charge * sim.ib_charge
    if sim.ib_charge > 0:
        i_dt_old_s *= sim.chemistry.coul_eff
        i_dt_new_s *= sim.chemistry.coul_eff
    if mon.reset:
        set_color(Colors.fg.red)
    elif sim.reset_temp_past:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 7, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(sim.reset_temp_past, None, 4, 0, 'rtps', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.sim_run.sat_s[G.i], sim.sat, 5, 0, 'sa_s', h, df)
        print_pair(SN.sim_run.dt_fut_s[G.i], sim.dt_fut_s, 12, 4, 'dt_fut_s', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 12, 4, 'dt', h, df)
        print_pair(SN.sim_run.dt_charge_s[G.i], sim.dt_charge, 12, 4, 'dt_charge_s', h, df)
        if hasattr(SN.sim_run, "dt_s"):
            print_pair(SN.sim_run.dt_s[G.i], sim.dt, 12, 4, 'dt_s', h, df)
        print_pair(SN.mon_run.ib[G.i], mon.ib, 14, 5, 'ib', h, df)
        print_pair(SN.sim_run.ib_s[G.i], mon.ib_s, 14, 5, 'ib_s', h, df)
        print_pair(SN.sim_run.ib_in_s[G.i], mon.ib_in_s, 16, 7, 'ib_in_s', h, df)
        print_pair(SN.sim_run.ib_fut_s[G.i], mon.ib_fut_s, 16, 7, 'ib_fut_s', h, df)
        print_pair(SN.mon_run.ib_charge[G.i], mon.ib_charge, 15, 6, 'ib_charge', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate[G.i], mon.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate[G.i], mon.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate', h, df)
        print_pair(SN.mon_run.ib_dyn_T[G.i], mon.ChargeTransfer.dt, 12, 4, 'ib_dyn_T', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 15, 7, 'ib_dyn', h, df)
        print_pair(SN.sim_run.ib_in_s[G.i], sim.ib_in, 14, 5, 'ib_in_s', h, df)
        print_pair(SN.sim_run.ib_s[G.i], sim.ib, 15, 6, 'ib_s', h, df)
        print_pair(SN.sim_run.ib_charge_s[G.i], sim.ib_charge, 15, 6, 'ib_charge_s', h, df)
        print_pair(SN.sim_run.ib_dyn_rstate_s[G.i], sim.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate_s', h, df)
        print_pair(SN.sim_run.ib_dyn_lstate_s[G.i], sim.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate_s', h, df)
        print_pair(SN.sim_run.ib_dyn_T_s[G.i], sim.ChargeTransfer.dt, 12, 4, 'ib_dyn_T_s', h, df)
        print_pair(SN.sim_run.ib_dyn_s[G.i], sim.ib_dyn, 15, 7, 'ib_dyn_s', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 15, 7, 'ib_dyn', h, df)
        print_pair(SN.sim_run.dv_hys_s[G.i], sim.dv_hys, 12, 5, 'dv_hys_s', h, df)
        print_pair(SN.mon_run.ib_charge[G.i], mon.ib_charge, 16, 7, 'ib_charge', h, df)
        print_pair(SN.sim_run.ib_fut_s[G.i], mon.ib_fut_s, 16, 7, 'ib_fut_s', h, df)
        print_pair(SN.sim_run.ib_charge_s[G.i], sim.ib_charge, 16, 7, 'ib_charge_s', h, df)
        print_pair(SN.sim_run.ioc_s[G.i], sim.ioc, 14, 5, 'ioc_s', h, df)
        print_pair(SN.mon_run.d_delta_q[G.i], mon.d_delta_q, 14, 7, 'd_delq', h, df)
        print_pair(i_dt_old, i_dt_new, 14, 7, 'i * dt * coul_eff', h, df)
        print_pair(SN.mon_run.delta_q[G.i], mon.delta_q, 16, 6, 'delq', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 13, 9, 'soc', h, df)
        print_pair(i_dt_old_s, i_dt_new_s, 14, 7, 'i * dt_s * coul_eff', h, df)
        print_pair(SN.sim_run.d_delta_q_s[G.i], sim.d_delta_q_s, 14, 7, 'd_delq_s', h, df)
        print_pair(SN.sim_run.delta_q_s[G.i], sim.delta_q_s, 16, 6, 'delq_s', h, df)
        print_pair(SN.sim_run.soc_s[G.i], sim.soc, 13, 9, 'soc_s', h, df)
        print_pair(SN.mon_run.Tb_model_f[G.i], None, 14, 8, 'Tb_model_f', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f[G.i], None, 14, 8, 'Tb_hdwe_f', h, df)
        print_pair(SN.sim_run.Tb_f_s[G.i], sim.Tb_f, 14, 8, 'Tb_f_s', h, df)
        print_pair(SN.sim_run.d_delta_q_s[G.i], sim.d_delta_q, 15, 6, 'd_delta_q_s', h, df)
        print_pair(SN.sim_run.delta_q_s[G.i], sim.delta_q, 15, 6, 'delta_q_s', h, df)
        print_pair(SN.mon_run.qcrs[G.i], mon.q_cap_rated_scaled, 12, 2, 'qcrs', h, df)
        print_pair(SN.mon_run.q_capacity[G.i], mon.q_capacity, 12, 2, 'q_cap', h, df)
        print_pair(SN.sim_run.qcap_s[G.i], sim.q_capacity, 12, 2, 'q_cap_s', h, df)
        print_pair(SN.sim_run.Tb_f_s[G.i], sim.Tb_f, 14, 7, 'Tb_f_s', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.Tb_f_rate[G.i], mon.Tb_f_rate, 12, 7, 'Tb_f_rate', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 11, 5, 'vb', h, df)
        print_pair(SN.sim_run.vb_s[G.i], sim.vb, 11, 5, 'vb_s', h, df)
        print_pair(SN.mon_run.voc_stat[G.i], mon.voc_stat, 11, 5, 'voc_stat', h, df)
        print_pair(SN.sim_run.voc_stat_s[G.i], sim.voc_stat, 11, 5, 'voc_stat_s', h, df)
        print_pair(SN.sim_run.voc_s[G.i], sim.voc, 11, 5, 'voc_s', h, df)
        print_pair(SN.sim_run.dv_hys_s[G.i], sim.dv_hys, 11, 5, 'dv_hys_s', h, df)
        print_pair(SN.sim_run.dv_dyn_s[G.i], sim.dv_dyn, 11, 5, 'dv_dyn_s', h, df)
        print_pair(SN.mon_run.vsat[G.i], mon.vsat, 11, 5, 'vsat', h, df)
        print_pair(bool(SN.sim_run.bms_off_s[G.i]), sim.bms_off, 7, 0, 'bms_off_s', h, df)
        print_pair(bool(SN.sim_run.voltage_low_s[G.i]), sim.voltage_low, 12, 0, 'voltage_low_s', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'

# 4
# noinspection PyPep8Naming
def print_temp_RunSim(SN, i_temp, t, mon, sim, calc_temp, i_ekf, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.sim_run, "Tb_f_s") or SN.sim_run.Tb_f_s is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_temp"
                f"_RunSim  (request_hist_in=4)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = calc_temp and count_since_last_header > HDR_SPREAD
    if calc_temp and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 7, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 3, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 2, 0, 'rk', h, df)
        print_pair(mon.mtb, None, 3, 0, 'mtb', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(SN.mon_run.Tb_hdwe[G.i], mon.Tb_hdwe, 13, 7, 'Tb_hdwe', h, df)
        print_pair(bool(SN.mon_run.Tb_flt[G.i]), mon.Tb_flt, 8, 0, 'Tb_flt', h, df)
        print_pair(bool(SN.mon_run.Tb_fa[G.i]), mon.Tb_fa, 8, 0, 'Tb_fa', h, df)
        print_pair(SN.mon_run.Tb[G.i], mon.Tb, 14, 7, 'Tb', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f[G.i], mon.Tb_hdwe_f, 14, 7, 'Tb_hdwe_f', h, df)
        print_pair(SN.mon_run.Tb_model[G.i], mon.Tb_model, 14, 7, 'Tb_model', h, df)
        print_pair(SN.mon_run.Tb_model_f[G.i], mon.Tb_model_f, 14, 7, 'Tb_model_f', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.sim_run.Tb_s[G.i], sim.Tb_s, 14, 7, 'Tb_s', h, df)
        print_pair(SN.sim_run.Tb_f_s[G.i], sim.Tb_f, 14, 7, 'Tb_f_s', h, df)
        print_pair(SN.mon_run.Tb_model_f_rate[G.i], mon.Tb_model_f_rate, 14, 7, 'Tb_model_f_rate', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f_rate[G.i], mon.Tb_hdwe_f_rate, 14, 7, 'Tb_hdwe_f_rate', h, df)
        print_pair(SN.mon_run.Tb_hdwe[G.i], mon.Tb_hdwe, 13, 7, 'Tb_hdwe', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f[G.i], mon.Tb_hdwe_f, 14, 7, 'Tb_hdwe_f', h, df)
        print_pair(SN.mon_run.dt_sel[G.i], mon.Tb_hdwe_f_dt, 14, 7, 'Tb_hdwe_f_dt', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f_tau[G.i], mon.Tb_hdwe_f_tau, 14, 7, 'Tb_hdwe_f_tau', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f_rstate[G.i], mon.Tb_hdwe_f_rstate, 14, 7, 'Tb_hdwe_f_rstate', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f_lstate[G.i], mon.Tb_hdwe_f_lstate, 14, 7, 'Tb_hdwe_f_lstate', h, df)
        print_pair(SN.mon_run.Tb_f_rate[G.i], mon.Tb_f_rate, 14, 7, 'Tb_f_rate', h, df)
        print_pair(SN.mon_run.Tb_hdwe_f[G.i], mon.Tb_hdwe_f, 14, 7, 'Tb_hdwe_f', h, df)
        print_pair(SN.mon_run.dt_sel[G.i], mon.Tb_model_f_dt, 14, 7, 'Tb_model_f_dt', h, df)
        print_pair(SN.mon_run.Tb_model_f_rstate[G.i], mon.Tb_model_f_rstate, 14, 7, 'Tb_model_f_rstate', h, df)
        print_pair(SN.mon_run.Tb_model_f_lstate[G.i], mon.Tb_model_f_lstate, 14, 7, 'Tb_model_f_lstate', h, df)
        print_pair(SN.mon_run.Tb_f_rate[G.i], mon.Tb_f_rate, 14, 7, 'Tb_f_rate', h, df)
        print_pair(SN.mon_run.tb_f_for_hx[i_ekf], mon.tb_f_for_hx, 14, 7, 'Tb_f_for_hx', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 5
# noinspection PyPep8Naming
def print_volt_HistSim(SN, i_temp, i_ekf, t, mon, calc_temp, calc_ekf, df=False):
    global count_since_last_header
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 4, 0, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 4, 0, 'rt', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(mon.reset_ekf, None, 4, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.vb_f[G.i], mon.vb, 11, 5, 'vb_f', h, df)
        print_pair(SN.mon_run.ib_f[G.i], mon.ib, 11, 5, 'ib_f', h, df)
        print_pair(SN.mon_run.ib_noa_hdwe_f[G.i], mon.LoopIbNoa.ib, 11, 5, 'ib_nh_f', h, df)
        print_pair(SN.mon_run.ib_amp_hdwe_f[G.i], mon.LoopIbAmp.ib, 11, 5, 'ib_mh_f', h, df)
        print_pair(SN.mon_run.ib_dyn_m[G.i], mon.LoopIbAmp.ib_dyn, 11, 5, 'ib_dyn_m', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 11, 5, 'e_wrap_n_filt', h, df)
        print_pair(SN.mon_run.e_wrap_m_filt[G.i], mon.e_wrap_m_filt, 11, 5, 'e_wrap_m_filt', h, df)
        print_pair(SN.mon_run.e_wrap_m_trim[G.i], mon.e_wrap_m_trim, 11, 5, 'e_wrap_m_trim', h, df)
        print_pair(SN.mon_run.ib_noa_hdwe_f[G.i], mon.LoopIbNoa.ib, 11, 5, 'ib_hn', h, df)
        print_pair(SN.mon_run.ib_dyn_n[G.i], mon.LoopIbNoa.ib_dyn, 11, 5, 'ib_dyn_n', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 11, 5, 'e_wrap_n_filt', h, df)
        print_pair(SN.mon_run.e_wrap_filt[G.i], mon.e_wrap_filt, 11, 5, 'e_wrap_filt', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 13, 7, 'soc', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 11, 4, 'dt', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.vb_f[G.i], mon.vb, 11, 5, 'vb_f', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 11, 5, 'ib_dyn', h, df)
        print_pair(SN.mon_run.voc_f[G.i], mon.voc, 11, 7, 'voc_f', h, df)
        print_pair(SN.mon_run.voc_stat_f[i_ekf], mon.voc_stat_f, 11, 7, 'voc_stat_f', h, df)
        print_pair(SN.mon_run.soc_ekf[G.i], mon.soc_ekf, 11, 5, 'soc_ekf', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 5
# noinspection PyPep8Naming
def print_volt_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "ib_amp_lo") or SN.mon_run.ib_amp_lo is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1 run.  Not printing print_volt_RunSim  (request_hist_in=5)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(bool(SN.mon_run.reset[G.i]), None, 7, 0, 'reset', h, df)
        print_pair(bool(SN.mon_run.reset_temp[G.i]), None, 10, 0, 'reset_temp', h, df)
        print_pair(bool(SN.mon_run.reset_all_faults[G.i]), None, 16, 0, 'reset_all_faults', h, df)
        print_pair(bool(SN.mon_run.soft_reset[G.i]), None, 15, 0, 'soft_reset', h, df)
        print_pair(bool(SN.mon_run.soft_reset_sim[G.i]), None, 15, 0, 'soft_reset_sim', h, df)
        print_pair(bool(SN.mon_run.init_mon[G.i]), None, 15, 0, 'init_mon', h, df)
        print_pair(bool(SN.mon_run.init_sim[G.i]), None, 15, 0, 'init_sim', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 13, 7, 'vb', h, df)
        print_pair(SN.mon_run.ib_charge[G.i], mon.ib_charge, 14, 6, 'ib_charge', h, df)
        print_pair(SN.mon_run.ib_sel[G.i], None, 14, 6, 'ib_sel', h, df)
        print_pair(SN.mon_run.ib[G.i], mon.ib, 14, 6, 'ib', h, df)
        print_pair(SN.mon_run.ib_amp_hdwe[G.i], mon.ib_amp_hdwe, 14, 6, 'ib_amp_hdwe', h, df)
        print_pair(SN.mon_run.ib_amp_model[G.i], mon.ib_amp_model, 14, 6, 'ib_amp_model', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], mon.ib_amp, 14, 6, 'ib_amp', h, df)
        print_pair(SN.mon_run.ib_noa_hdwe[G.i], mon.ib_noa_hdwe, 14, 6, 'ib_noa_hdwe', h, df)
        print_pair(SN.mon_run.ib_noa_model[G.i], mon.ib_noa_model, 14, 6, 'ib_noa_model', h, df)
        print_pair(SN.mon_run.ib_noa[G.i], mon.ib_noa, 14, 6, 'ib_noa', h, df)
        print_pair(bool(SN.mon_run.disable_amp_fault[G.i]), bool(mon.disable_amp_fault), 10, 0, 'disable_amp_fault', h, df)
        print_pair(SN.mon_run.ib_diff[G.i], mon.ib_diff, 14, 6, 'ib_diff', h, df)
        print_pair(SN.mon_run.ib_diff_flt[G.i], mon.Diff.ib_diff_hi_flt or mon.Diff.ib_diff_lo_flt, 8, 0, 'ib_diff_flt', h, df)
        print_pair(bool(SN.mon_run.ib_lo_active[G.i]), mon.ib_lo_active, 8, 0, 'ib_lo_active', h, df)
        print_pair("x", mon.Diff.ib_lo_limited_hi, 10, 0, 'ib_lo_limited_hi', h, df)
        print_pair("x", mon.Diff.ib_lo_limited_lo, 10, 0, 'ib_lo_limited_lo', h, df)
        print_pair(SN.mon_run.ib_h[G.i], mon.ib_hdwe, 20, 6, 'ibh', h, df)
        print_pair(SN.mon_run.ib_s[G.i], sim.ib, 14, 6, 'ib_s', h, df)
        print_pair(mon.ib_amp_model, None, 12, 6, 'ib_amp_model', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], None, 14, 6, 'ib_amp', h, df)
        print_pair(bool(SN.mon_run.ib_amp_lo[G.i]), bool(mon.ib_amp_lo), 7, 0, 'ib_amp_lo', h, df)
        print_pair(bool(SN.mon_run.ib_amp_hi[G.i]), bool(mon.ib_amp_hi), 7, 0, 'ib_amp_hi', h, df)
        print_pair(bool(SN.mon_run.ib_noa_lo[G.i]), bool(mon.ib_noa_lo), 7, 0, 'ib_noa_lo', h, df)
        print_pair(bool(SN.mon_run.ib_noa_hi[G.i]), bool(mon.ib_noa_hi), 7, 0, 'ib_noa_hi', h, df)
        print_pair(bool(SN.mon_run.disable_amp_fault[G.i]), bool(mon.disable_amp_fault), 7, 0, 'dis_amp_flt', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 11, 4, 'dt', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], mon.ib_amp, 14, 6, 'ib_amp', h, df)
        print_pair(SN.mon_run.ib_dyn_T_m[G.i], mon.LoopIbAmp.ChargeTransfer.dt, 9, 4, 'ib_dyn_T_m', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate_m[G.i], mon.LoopIbAmp.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate_m', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate_m[G.i], mon.LoopIbAmp.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate_m', h, df)
        print_pair(SN.mon_run.ib_dyn_m[G.i], mon.LoopIbAmp.ib_dyn, 21, 6, 'ib_dyn_m', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 11, 5, 'vb', h, df)
        print_pair(SN.mon_run.vb_model[G.i], mon.vb_model, 11, 5, 'vb_model', h, df)
        print_pair(SN.mon_run.vb_hdwe[G.i], mon.vb_hdwe, 11, 5, 'vb_hdwe', h, df)
        print_pair(SN.mon_run.vb_hdwe_f[G.i], mon.vb_hdwe_f, 11, 5, 'vb_hdwe_f', h, df)
        print_pair(SN.mon_run.dv_dyn_m[G.i], mon.LoopIbAmp.dv_dyn, 11, 5, 'dv_dyn_m', h, df)
        print_pair(SN.mon_run.ib_wrp_T_m[G.i], mon.LoopIbAmp.WrapErrFilt.dt, 12, 4, 'e_wrap_m_T', h, df)
        print_pair(SN.mon_run.ib_wrp_tau_m[G.i], mon.LoopIbAmp.WrapErrFilt.tau, 12, 4, 'e_wrap_m_tau', h, df)
        print_pair(SN.mon_run.ib_wrp_rate_m[G.i], mon.LoopIbAmp.WrapErrFilt.rate, 12, 6, 'e_wrap_m_rate', h, df)
        print_pair(bool(SN.mon_run.ib_wrp_reset_m[G.i]), bool(mon.LoopIbAmp.WrapErrFilt.reset), 12, 0, 'e_wrap_m_reset', h, df)
        print_pair(SN.mon_run.ib_wrp_state_m[G.i], mon.LoopIbAmp.WrapErrFilt.state, 12, 6, 'e_wrap_m_state', h, df)
        print_pair(SN.mon_run.voc[G.i], mon.voc, 11, 5, 'voc', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 11, 5, 'voc_soc', h, df)
        print_pair(SN.mon_run.e_wrap_m[G.i], mon.e_wrap_m, 11, 5, 'e_wrap_m', h, df)
        print_pair(SN.mon_run.e_wrap_m_filt[G.i], mon.e_wrap_m_filt, 11, 5, 'e_wrap_m_filt', h, df)
        print_pair(SN.mon_run.disable_amp_fault[G.i], mon.disable_amp_fault, 13, 0, 'disable_amp_fault', h, df)
        print_pair(mon.ib_amp_lo, None, 10, 0, 'ib_amp_lo', h, df)
        print_pair(mon.ib_noa_lo, None, 10, 0, 'ib_noa_lo', h, df)
        print_pair(SN.mon_run.e_wrap_m_reset[G.i], mon.e_wrap_m_reset, 26, 0, 'e_wrap_m_reset', h, df)
        print_pair(SN.mon_run.e_wrap_m_trim[G.i], mon.e_wrap_m_trim, 16, 5, 'e_wrap_m_trim', h, df)
        print_pair(SN.mon_run.ib_dyn_n[G.i], mon.LoopIbNoa.ib_dyn, 14, 6, 'ib_dyn_n', h, df)
        print_pair(SN.mon_run.ib_dyn_T_n[G.i], mon.LoopIbNoa.ChargeTransfer.dt, 9, 4, 'ib_dyn_T_n', h, df)
        print_pair(SN.mon_run.dv_dyn_n[G.i], mon.LoopIbNoa.dv_dyn, 11, 6, 'dv_dyn_n', h, df)
        print_pair(SN.mon_run.e_wrap_n[G.i], mon.e_wrap_n, 11, 5, 'e_wrap_n', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 11, 5, 'e_wrap_n_filt', h, df)
        print_pair(SN.mon_run.ib_dyn_n[G.i], mon.LoopIbNoa.ib_dyn, 14, 6, 'ib_dyn_n', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 14, 6, 'ib_dyn', h, df)
        print_pair(SN.mon_run.ib_dyn_T_n[G.i], mon.LoopIbNoa.ChargeTransfer.dt, 9, 4, 'ib_dyn_T_n', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate_n[G.i], mon.LoopIbNoa.ChargeTransfer.rstate, 15, 6, 'ib_dyn_rstate_n', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate_n[G.i], mon.LoopIbNoa.ChargeTransfer.state, 15, 6, 'ib_dyn_lstate_n', h, df)
        print_pair(SN.mon_run.dv_dyn_n[G.i], mon.LoopIbNoa.dv_dyn, 11, 5, 'dv_dyn_n', h, df)
        print_pair(SN.mon_run.ib_wrp_T_n[G.i], mon.LoopIbNoa.WrapErrFilt.dt, 12, 4, 'e_wrap_n_T', h, df)
        print_pair(SN.mon_run.ib_wrp_tau_n[G.i], mon.LoopIbNoa.WrapErrFilt.tau, 12, 4, 'e_wrap_n_tau', h, df)
        print_pair(SN.mon_run.ib_wrp_rate_n[G.i], mon.LoopIbNoa.WrapErrFilt.rate, 12, 6, 'e_wrap_n_rate', h, df)
        print_pair(SN.mon_run.ib_wrp_state_n[G.i], mon.LoopIbNoa.WrapErrFilt.state, 12, 6, 'e_wrap_n_state', h, df)
        print_pair(SN.mon_run.e_wrap_n_trim[G.i], mon.e_wrap_n_trim, 16, 5, 'e_wrap_n_trim', h, df)
        print_pair(SN.mon_run.e_wrap_n_trimmed[G.i], mon.LoopIbNoa.e_wrap_trimmed, 12, 6, 'e_wrap_n_trimmed', h, df)
        print_pair(SN.mon_run.e_wrap_n[G.i], mon.e_wrap_n, 11, 5, 'e_wrap_n', h, df)
        print_pair(SN.mon_run.e_wrap_n_filt[G.i], mon.e_wrap_n_filt, 11, 5, 'e_wrap_n_filt', h, df)
        print_pair(SN.mon_run.ib[G.i], mon.ib, 14, 6, 'ib', h, df)
        print_pair(SN.mon_run.e_wrap[G.i], mon.e_wrap, 11, 5, 'e_wrap', h, df)
        print_pair(SN.mon_run.e_wrap_filt[G.i], mon.e_wrap_filt, 11, 5, 'e_wrap_filt', h, df)
        print_pair(bool(SN.mon_run.ib_dyn_r[G.i]), mon.ib_dyn_r, 6, 0, 'ib_dyn_r', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate[G.i], mon.ib_dyn_in, 15, 6, 'ib_dyn_in', h, df)
        print_pair(SN.mon_run.ib_dyn_T[G.i], mon.ib_dyn_T, 15, 6, 'ib_dyn_T', h, df)
        print_pair(SN.mon_run.ib_dyn_rstate[G.i], mon.ib_dyn_rstate, 15, 6, 'ib_dyn_rstate', h, df)
        print_pair(SN.mon_run.ib_dyn_lstate[G.i], mon.ib_dyn_lstate, 15, 6, 'ib_dyn_lstate', h, df)
        print_pair(SN.mon_run.ib_dyn[G.i], mon.ib_dyn, 15, 6, 'ib_dyn', h, df)
        print_pair(SN.mon_run.dv_dyn[G.i], mon.dv_dyn, 14, 6, 'dv_dyn', h, df)
        print_pair(SN.mon_run.dv_hys[G.i], mon.dv_hys, 12, 6, 'dv_hys', h, df)
        print_pair(SN.mon_run.soc[G.i], mon.soc, 13, 7, 'soc', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 9, 4, 'dt', h, df)
        print_pair(SN.mon_run.Tb_f[G.i], mon.Tb_f, 14, 7, 'Tb_f', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 11, 5, 'voc_soc', h, df)
        print_pair(SN.mon_run.voc[G.i], mon.voc, 11, 5, 'voc', h, df)
        print_pair(SN.mon_run.voc_stat[G.i], mon.voc_stat, 11, 5, 'voc_stat', h, df)
        print_pair(SN.sim_run.voc_stat_s[G.i], sim.voc_stat, 11, 5, 'voc_stat_s', h, df)
        print_pair(SN.mon_run.voc_stat_f[i_ekf], mon.voc_stat_f, 11, 5, 'voc_stat_f', h, df)
        print_pair(SN.mon_run.soc_ekf[G.i], mon.soc_ekf, 11, 5, 'soc_ekf', h, df)
        print_pair(SN.mon_run.y_ekf[G.i], mon.y_ekf, 11, 5, 'y_ekf', h, df)
        print_pair(SN.mon_run.y_ekf_f[G.i], mon.y_ekf_f, 11, 5, 'y_ekf_f', h, df)
        print_pair(SN.mon_run.fltw[G.i], None, 8, 0, 'fltw', h, df)
        print_pair(SN.mon_run.falw[G.i], None, 4, 0, 'falw', h, df)
        print_pair(SN.mon_run.soc_min[G.i], mon.soc_min, 11, 5, 'soc_min', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 8
# noinspection PyPep8Naming
def print_vb_wrap_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "voltage_low") or SN.mon_run.voltage_low is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_vb_w"
                f"rap_RunSim  (request_hist_in=8)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(bool(SN.mon_run.reset[G.i]), None, 7, 0, 'reset', h, df)
        print_pair(bool(SN.mon_run.reset_temp[G.i]), None, 10, 0, 'reset_temp', h, df)
        print_pair(bool(SN.mon_run.reset_all_faults[G.i]), None, 16, 0, 'reset_all_faults', h, df)
        print_pair(bool(SN.mon_run.soft_reset[G.i]), None, 15, 0, 'soft_reset', h, df)
        print_pair(bool(SN.mon_run.soft_reset_sim[G.i]), None, 15, 0, 'soft_reset_sim', h, df)
        print_pair(bool(SN.mon_run.init_mon[G.i]), None, 15, 0, 'init_mon', h, df)
        print_pair(bool(SN.mon_run.init_sim[G.i]), None, 15, 0, 'init_sim', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(bool(SN.mon_run.bms_off[G.i]), bool(mon.bms_off), 7, 0, 'bms_off', h, df)
        print_pair(bool(SN.mon_run.voltage_low[G.i]), bool(mon.voltage_low), 7, 0, 'voltage_low', h, df)
        print_pair(bool(SN.sim_run.bms_off_s[G.i]), bool(sim.bms_off), 7, 0, 'bms_off_s', h, df)
        print_pair(bool(SN.sim_run.voltage_low_s[G.i]), bool(sim.voltage_low), 7, 0, 'voltage_low_s', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 10, 4, 'dt', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 13, 7, 'vb', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], mon.ib_amp, 15, 6, 'ib_amp', h, df)
        print_pair(SN.mon_run.vb_model[G.i], mon.LoopIbAmp.vb, 13, 6, 'vb_m', h, df)
        print_pair(SN.mon_run.voc_m[G.i], mon.LoopIbAmp.voc, 13, 6, 'voc_m', h, df)
        print_pair(SN.mon_run.voc_soc_m[G.i], mon.LoopIbAmp.voc_soc, 11, 6, 'voc_soc_m', h, df)
        print_pair(SN.mon_run.voc_soc[G.i], mon.voc_soc, 13, 6, 'voc_soc', h, df)
        print_pair(SN.mon_run.e_wrap_m[G.i], mon.e_wrap_m, 13, 5, 'e_wrap_m', h, df)
        print_pair(SN.mon_run.e_wrap_m_trim[G.i], mon.e_wrap_m_trim, 16, 5, 'e_wrap_trim', h, df)
        print_pair(SN.mon_run.e_wrap_m_trimmed[G.i], mon.LoopIbAmp.e_wrap_trimmed, 12, 6, 'e_wrap_trimmed', h, df)
        print_pair(SN.mon_run.e_wrap_m_filt[G.i], mon.e_wrap_m_filt, 11, 5, 'e_wrap_m_filt', h, df)
        print_pair(SN.mon_run.ib_diff_fa[G.i], None, 10, 0, 'ib_diff_fa', h, df)
        print_pair(SN.mon_run.wrap_m_and_n_fa[G.i], None, 15, 0, 'wrap_m_and_n_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_m_flt[G.i], mon.wrap_lo_m_flt, 16, 0, 'wrap_lo_m_flt', h, df)
        print_pair(SN.mon_run.wrap_lo_m_fa[G.i], mon.wrap_lo_m_fa, 11, 0, 'wrap_lo_m_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_n_fa[G.i], mon.wrap_lo_n_fa, 11, 0, 'wrap_lo_n_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_fa[G.i], None, 14, 0, 'wrap_lo_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_m_fa[G.i], mon.wrap_hi_m_fa, 14, 0, 'wrap_hi_m_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_n_fa[G.i], mon.wrap_hi_n_fa, 14, 0, 'wrap_hi_n_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_fa[G.i], None, 14, 0, 'wrap_hi_fa', h, df)
        print_pair(SN.mon_run.ib_is_functional[G.i], None, 18, 0, 'ib_is_functional', h, df)
        print_pair(SN.mon_run.wv_fa[G.i], None, 18, 0, 'wrap_vb_faj', h, df)
        print_pair(bool(SN.mon_run.ib_quiet[G.i]), None, 18, 0, 'ib_quiet', h, df)
        print_pair(bool(SN.mon_run.ib_really_quiet[G.i]), None, 18, 0, 'ib_really_quiet', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


# 10
# noinspection PyPep8Naming
def print_cc_diff_RunSim(SN, i_temp, i_ekf, t, mon, sim, calc_temp, calc_ekf, df=False):
    global count_since_last_header, vv_warning_printed
    if not hasattr(SN.mon_run, "voltage_low") or SN.mon_run.voltage_low is None:
        if not vv_warning_printed:
            print(Colors.fg.red, end="")
            print(
                f"\n**********\nLikely a vv1-vv3 run.  Not printing print_cc_d"
                f"iff_RunSim  (request_hist_in=10)\n*************\n"
            )
            vv_warning_printed = True
            print(Colors.reset, end="")
        return None
    print_hdr = (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD
    if (calc_temp or calc_ekf) and count_since_last_header > HDR_SPREAD:
        count_since_last_header = 0
    if G.i > 0:
        count_since_last_header += 1
    if mon.reset:
        set_color(Colors.fg.red)
    elif mon.reset_temp:
        set_color(Colors.fg.orange)
    else:
        set_color(Colors.reset)

    for i_hdr in range(int(print_hdr), -1, -1):
        h = (i_hdr == 1)
        print_pair(G.i, None, 4, 0, 'i', h, df)
        print_pair(t[G.i], None, 8, 3, 'time', h, df)
        print_pair(mon.reset, None, 2, 0, 'r', h, df)
        print_pair(mon.reset_temp, None, 7, 0, 'rt', h, df)
        print_pair(mon.reset_kf, None, 4, 0, 'rk', h, df)
        print_pair(i_temp, None, 4, 0, 'it', h, df)
        print_pair(calc_temp, None, 4, 0, 'ct', h, df)
        print_pair(mon.reset_ekf, None, 7, 0, 're', h, df)
        print_pair(i_ekf, None, 4, 0, 'ie', h, df)
        print_pair(calc_ekf, None, 4, 0, 'ce', h, df)
        print_pair(bool(SN.mon_run.reset[G.i]), None, 7, 0, 'reset', h, df)
        print_pair(bool(SN.mon_run.reset_temp[G.i]), None, 10, 0, 'reset_temp', h, df)
        print_pair(bool(SN.mon_run.reset_all_faults[G.i]), None, 16, 0, 'reset_all_faults', h, df)
        print_pair(bool(SN.mon_run.soft_reset[G.i]), None, 15, 0, 'soft_reset', h, df)
        print_pair(bool(SN.mon_run.soft_reset_sim[G.i]), None, 15, 0, 'soft_reset_sim', h, df)
        print_pair(bool(SN.mon_run.init_mon[G.i]), None, 15, 0, 'init_mon', h, df)
        print_pair(bool(SN.mon_run.init_sim[G.i]), None, 15, 0, 'init_sim', h, df)
        print_pair(SN.mon_run.sat[G.i], mon.sat, 4, 0, 'sa', h, df)
        print_pair(bool(SN.mon_run.bms_off[G.i]), bool(mon.bms_off), 7, 0, 'bms_off', h, df)
        print_pair(bool(SN.mon_run.voltage_low[G.i]), bool(mon.voltage_low), 7, 0, 'voltage_low', h, df)
        print_pair(bool(SN.sim_run.bms_off_s[G.i]), bool(sim.bms_off), 7, 0, 'bms_off_s', h, df)
        print_pair(bool(SN.sim_run.voltage_low_s[G.i]), bool(sim.voltage_low), 7, 0, 'voltage_low_s', h, df)
        print_pair(SN.mon_run.dt[G.i], mon.dt, 10, 4, 'dt', h, df)
        print_pair(SN.mon_run.vb[G.i], mon.vb, 13, 7, 'vb', h, df)
        print_pair(SN.mon_run.ib_amp[G.i], mon.ib_amp, 15, 6, 'ib_amp', h, df)

        # Coulomb counter, EKF SOC & cc_diff fault logic parameters
        soc_val = SN.mon_run.soc[G.i] if hasattr(SN.mon_run, "soc") and SN.mon_run.soc is not None else None
        soc_ekf_val = SN.mon_run.soc_ekf[G.i] if hasattr(SN.mon_run, "soc_ekf") and SN.mon_run.soc_ekf is not None else None
        mon_soc_val = getattr(mon, "soc", None)
        mon_soc_ekf_val = getattr(mon, "soc_ekf", None)

        if hasattr(SN.mon_run, "cc_dif") and SN.mon_run.cc_dif is not None:
            run_cc_dif = SN.mon_run.cc_dif[G.i]
        elif soc_val is not None and soc_ekf_val is not None:
            run_cc_dif = soc_ekf_val - soc_val
        else:
            run_cc_dif = None

        if hasattr(mon, "cc_dif") and mon.cc_dif is not None:
            mon_cc_dif = mon.cc_dif
        elif mon_soc_val is not None and mon_soc_ekf_val is not None:
            mon_cc_dif = mon_soc_ekf_val - mon_soc_val
        else:
            mon_cc_dif = None

        if hasattr(SN.mon_run, "cc_diff_thr") and SN.mon_run.cc_diff_thr is not None:
            run_cc_diff_thr = SN.mon_run.cc_diff_thr[G.i]
        else:
            run_cc_diff_thr = getattr(mon, "cc_diff_thr", 0.2)

        mon_cc_diff_thr = getattr(mon, "cc_diff_thr", 0.2)

        run_ccd_flt = bool(SN.mon_run.ccd_flt[G.i]) if hasattr(SN.mon_run, "ccd_flt") and SN.mon_run.ccd_flt is not None else False
        mon_ccd_flt = bool(getattr(mon, "ccd_flt", False))

        run_ccd_fa = bool(SN.mon_run.ccd_fa[G.i]) if hasattr(SN.mon_run, "ccd_fa") and SN.mon_run.ccd_fa is not None else False
        mon_ccd_fa = bool(getattr(mon, "ccd_fa", False))

        run_flt_ekf = bool(SN.mon_run.flt_ekf[G.i]) if hasattr(SN.mon_run, "flt_ekf") and SN.mon_run.flt_ekf is not None else False
        mon_flt_ekf = bool(getattr(mon, "flt_ekf", False))

        print_pair(soc_val, mon_soc_val, 13, 6, 'soc', h, df)
        print_pair(soc_ekf_val, mon_soc_ekf_val, 13, 6, 'soc_ekf', h, df)
        print_pair(run_cc_dif, mon_cc_dif, 13, 6, 'cc_dif', h, df)
        print_pair(run_cc_diff_thr, mon_cc_diff_thr, 13, 6, 'cc_diff_thr', h, df)
        print_pair(run_ccd_flt, mon_ccd_flt, 10, 0, 'ccd_flt', h, df)
        print_pair(run_ccd_fa, mon_ccd_fa, 10, 0, 'ccd_fa', h, df)
        print_pair(run_flt_ekf, mon_flt_ekf, 10, 0, 'flt_ekf', h, df)

        print_pair(SN.mon_run.ib_diff_fa[G.i], None, 10, 0, 'ib_diff_fa', h, df)
        print_pair(SN.mon_run.wrap_m_and_n_fa[G.i], None, 15, 0, 'wrap_m_and_n_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_m_flt[G.i], mon.wrap_lo_m_flt, 16, 0, 'wrap_lo_m_flt', h, df)
        print_pair(SN.mon_run.wrap_lo_m_fa[G.i], mon.wrap_lo_m_fa, 11, 0, 'wrap_lo_m_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_n_fa[G.i], mon.wrap_lo_n_fa, 11, 0, 'wrap_lo_n_fa', h, df)
        print_pair(SN.mon_run.wrap_lo_fa[G.i], None, 14, 0, 'wrap_lo_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_m_fa[G.i], mon.wrap_hi_m_fa, 14, 0, 'wrap_hi_m_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_n_fa[G.i], mon.wrap_hi_n_fa, 14, 0, 'wrap_hi_n_fa', h, df)
        print_pair(SN.mon_run.wrap_hi_fa[G.i], None, 14, 0, 'wrap_hi_fa', h, df)
        print_pair(SN.mon_run.ib_is_functional[G.i], None, 18, 0, 'ib_is_functional', h, df)
        print_pair(SN.mon_run.wv_fa[G.i], None, 18, 0, 'wrap_vb_faj', h, df)
        print_pair(bool(SN.mon_run.ib_quiet[G.i]), None, 18, 0, 'ib_quiet', h, df)
        print_pair(bool(SN.mon_run.ib_really_quiet[G.i]), None, 18, 0, 'ib_really_quiet', h, df, end="\n")

    print(Colors.reset, end="")
    return 'header'


def save_clean_file(mon_ver, csv_file, unit_key):
    if mon_ver is None:
        print("save_clean_file: mon_ver is None (broke early due to skip), skipping save.")
        return
    default_header_str = (
        "unit,               hm,                  c_time,        dt,       sat,sel,mod,"
        "      Tb,Tb_rap,Tb_f,Tb_f,Tb_f_rate,Tb_f_rate_rap, vb,  ib,  ib_dyn, ioc,  voc_soc,"
        "    vsat,dv_dyn,voc_stat,voc_stat_f,voc_ekf,     y,    soc_s,soc_ekf,soc,ib_lag,voc_soc_new,"
    )
    n = len(mon_ver.time)
    date_time_start = datetime.now()
    with open(csv_file, "w") as output:
        output.write(default_header_str + "\n")
        for i in range(n):
            s = unit_key + ","
            dt_dt = timedelta(seconds=mon_ver.time[i] - mon_ver.time[0])
            time_stamp = date_time_start + dt_dt
            s += time_stamp.strftime("%Y-%m-%dT%H:%M:%S,")
            s += "{:7.4f},".format(mon_ver.time[i] + mon_ver.time_run_start)
            s += "{:7.4f},".format(mon_ver.dt[i])
            s += "{:1.0f},".format(mon_ver.sat[i])
            # s += "{:1.0f},".format(mon_ver.sel[i])
            s += "{:1.0f},".format(mon_ver.mod_data[i])
            s += "{:7.6f},".format(mon_ver.Tb[i])
            s += "{:7.6f},".format(mon_ver.Tb_f[i])
            s += "{:7.6f},".format(mon_ver.Tb_f[i])
            s += "{:7.6f},".format(mon_ver.Tb_f_rate[i])
            s += "{:7.3f},".format(mon_ver.vb[i])
            s += "{:7.3f},".format(mon_ver.ib[i])
            s += "{:7.3f},".format(mon_ver.ib_dyn[i])
            s += "{:7.3f},".format(mon_ver.ioc[i])
            s += "{:7.3f},".format(mon_ver.voc_soc[i])
            s += "{:7.3f},".format(mon_ver.vsat[i])
            s += "{:7.3f},".format(mon_ver.dv_dyn[i])
            s += "{:7.3f},".format(mon_ver.voc_stat[i])
            s += "{:7.3f},".format(getattr(mon_ver, "voc_stat_f", mon_ver.voc_stat)[i])
            s += "{:7.3f},".format(mon_ver.voc_ekf[i])
            s += "{:7.3f},".format(mon_ver.y[i])
            s += "{:7.3f},".format(mon_ver.soc_s[i])
            s += "{:7.3f},".format(mon_ver.soc_ekf[i])
            s += "{:7.3f},".format(mon_ver.soc[i])
            s += "{:7.5f},".format(mon_ver.ib_lag[i])
            s += "{:7.3f},".format(mon_ver.voc_soc_new[i])
            s += "\n"
            output.write(s)
        print("Wrote(save_clean_file):", csv_file)


def save_clean_file_sim(sim_ver, csv_file, unit_key):
    header_str = "unit_m,c_time,Tb_s,vsat_s,voc_stat_s,dv_dyn_s,vb_s,ib_s,sat_s,delta_q_s,\
    soc_s,reset_s,"
    n = len(sim_ver.time)
    with open(csv_file, "w") as output:
        output.write(header_str + "\n")
        for i in range(n):
            s = unit_key + ","
            s += "{:13.3f},".format(sim_ver.time[i])
            s += "{:5.2f},".format(sim_ver.Tb_s[i])
            s += "{:8.3f},".format(sim_ver.vsat_s[i])
            s += "{:5.2f},".format(sim_ver.voc_stat_s[i])
            s += "{:5.2f},".format(sim_ver.dv_dyn_s[i])
            s += "{:5.2f},".format(sim_ver.vb_s[i])
            s += "{:8.3f},".format(sim_ver.ib_s[i])
            s += "{:7.3f},".format(sim_ver.sat_s[i])
            s += "{:5.3f},".format(sim_ver.dq_s[i])
            s += "{:7.3f},".format(sim_ver.soc_s[i])
            s += "{:7.3f},".format(sim_ver.reset_s[i])
            s += "\n"
            output.write(s)
        print("Wrote(save_clean_file_sim):", csv_file)


def save_fault_coverage(mon_run, csv_file, unit_key):
    hdr_list = ["unit_fault", "hm"]
    flt_list = [
        "fltw",
        "falw",
        "ccd_fa",
        "ib_diff_flt",
        "ib_diff_fa",
        "wrap_hi_flt",
        "wrap_lo_flt",
        "vc_flt",
        "wrap_hi_m_flt",
        "wrap_lo_m_flt",
        "wrap_hi_n_flt",
        "wrap_lo_n_flt",
        "wrap_m_and_n_flt",
        "red_loss",
        "wrap_hi_fa",
        "wrap_lo_fa",
        "wv_fa",
        "vc_fa",
        "wrap_hi_m_fa",
        "wrap_lo_m_fa",
        "wrap_hi_n_fa",
        "wrap_lo_n_fa",
        "wrap_m_and_n_fa",
        "ib_sel",
        "ib_noa_bare_flt",
        "ib_amp_bare_flt",
        "ib_dscn_flt",
        "ib_dscn_fa",
        "ib_noa_flt",
        "ib_noa_fa",
        "ib_amp_flt",
        "ib_amp_fa",
        "vb_flt",
        "vb_fa_lt",
        "Tb_flt",
        "Tb_fa",
        "bms_off",
        "sat",
        "red_loss",
    ]
    default_header_str = ""
    import numpy as np

    m = 0
    flt_data = []
    mon_run.wrap_m_and_n_flt = (np.bool(mon_run.wrap_lo_n_flt) & np.bool(mon_run.wrap_lo_m_flt)) | (
        np.bool(mon_run.wrap_hi_n_flt) & np.bool(mon_run.wrap_hi_m_flt)
    )
    mon_run.wrap_m_and_n_fa = (np.bool(mon_run.wrap_lo_n_fa) & np.bool(mon_run.wrap_lo_m_fa)) | (
        np.bool(mon_run.wrap_hi_n_fa) & np.bool(mon_run.wrap_hi_m_fa)
    )
    for flt in hdr_list:
        default_header_str += flt + ","
    for flt in flt_list:
        default_header_str += flt + ","
        flt_data.append(getattr(mon_run, flt))
        m += 1
    n = len(mon_run.time)
    date_time_start = datetime.now()
    with open(csv_file, "w") as output:
        output.write(default_header_str + "\n")
        for i in range(n):
            s = unit_key + ","
            dt_dt = timedelta(seconds=mon_run.time[i] - mon_run.time[0])
            time_stamp = date_time_start + dt_dt
            s += time_stamp.strftime("%Y-%m-%dT%H:%M:%S,")
            for j in range(m):
                s += "{:2d},".format(np.bool(flt_data[j][i]))
            s += "\n"
            output.write(s)
        s = "covered: "
        for j in range(m):
            if any(flt_data[j][:] == 1):
                s += flt_list[j] + ","
        s += "\n"
        output.write(s)

    print("Wrote(save_fault_coverage):", csv_file)
