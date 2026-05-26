# MonSim:  Monitor and Simulator replication of Particle Photon Application
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

""" Python model of what's installed on the Particle Photon.  Includes
a monitor object (MON) and a simulation object (SIM).   The monitor is
the EKF and Coulomb Counter.   The SIM is a battery model, that also has a
Coulomb Counter built in."""

import math
import os
import traceback

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path, PurePosixPath

from DataOverModel import dom_plot
from CompareFault import over_fault
from unite_pictures import cleanup_fig_files
from PlotKiller import show_killer
from load_data import load_data, calculate_master_sync
from local_paths import version_from_data_path, version_from_data_file, local_paths
from plot.PlotOptions import PlotOptions

# Suppress all UserWarning messages
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# ── EWMA difference helpers ───────────────────────────────────────────────────
#
# Two hardware runs of the same experiment differ by random *timing jitter*:
# each sample arrives slightly early or late, creating instantaneous sign-
# alternating spikes in (run - test).  RMS would square those spikes and
# amplify them.  Instead we use an EWMA (Exponentially Weighted Moving
# Average) — the digital equivalent of a first-order RC low-pass filter —
# which preserves sign so that zero-mean jitter noise averages to zero while
# a *persistent systematic offset* accumulates and stays visible.
#
# Reference: Hunter (1986) "The Exponentially Weighted Moving Average,"
# Journal of Quality Technology 18(4); Montgomery "Introduction to
# Statistical Quality Control," EWMA control charts chapter.

def _running_avg(diff, time, tau):
    """EWMA (first-order IIR low-pass) of a signed difference signal.

        avg[0]  = diff[0]
        avg[n]  = (1 - alpha_n) * avg[n-1]  +  alpha_n * diff[n]
        alpha_n = 1 - exp(-dt_n / tau)

    alpha adapts from the actual inter-sample interval dt_n so non-uniform
    hardware sampling is handled correctly.  tau is the time constant in
    seconds — larger tau → more smoothing → only slow, persistent offsets
    remain above the threshold.
    """
    n = len(diff)
    if n == 0:
        return np.zeros(0, dtype=float)
    avg = np.empty(n, dtype=float)
    avg[0] = 0.0
    for i in range(1, n):
        dt = max(float(time[i] - time[i - 1]), 1e-9)
        alpha = 1.0 - np.exp(-dt / tau)
        avg[i] = (1.0 - alpha) * avg[i - 1] + alpha * float(diff[i])
    return avg


def compare_pair_rms(run_path, ver_path, tol=1e-3, rtol=1e-3, tau=60.0):
    """Compare two run CSVs via EWMA of the signed difference.

    A column is flagged when  max(|ewma_series|) > tol + rtol * peak,
    where peak = column-wise max(|run|, |test|).  Because EWMA preserves
    sign, timing-jitter noise (zero-mean, alternating) averages to zero
    and does not trip the threshold; only systematic persistent offsets do.

    Returns a result dict for report_rms / plot_rms_diffs.
    """
    try:
        df_run = pd.read_csv(run_path)
        df_ver = pd.read_csv(ver_path)
    except Exception as e:
        return {'file': run_path.name, 'ver_file': ver_path.name, 'error': str(e), 'diffs': []}

    # locate time column — raw clean files use 'cTime'; processed files use 'time'
    _time_col = next((c for c in ('time', 'cTime') if c in df_run.columns and c in df_ver.columns), None)
    if _time_col is None:
        return {'file': run_path.name, 'ver_file': ver_path.name,
                'error': 'no "time" or "cTime" column found', 'diffs': []}

    df_run = df_run[pd.to_numeric(df_run[_time_col], errors='coerce') >= 0].copy()
    df_ver = df_ver[pd.to_numeric(df_ver[_time_col], errors='coerce') >= 0].copy()
    n = min(len(df_run), len(df_ver))
    if n == 0:
        return {'file': run_path.name, 'ver_file': ver_path.name,
                'error': 'no rows with time >= 0', 'diffs': []}
    df_run = df_run.iloc[:n].reset_index(drop=True)
    df_ver = df_ver.iloc[:n].reset_index(drop=True)

    shared = [c for c in df_run.columns if c in df_ver.columns]
    _nan_frac = 0.5  # skip columns where more than this fraction of rows are NaN in either file
    numeric_cols = [c for c in shared
                    if c != _time_col
                    and not c.startswith('skip')   # write_clean_file adds a leading skip_* column
                    and pd.api.types.is_float_dtype(df_run[c])
                    and pd.api.types.is_float_dtype(df_ver[c])
                    and df_run[c].isna().mean() <= _nan_frac
                    and df_ver[c].isna().mean() <= _nan_frac]

    time_arr = df_run[_time_col].values.astype(float)
    diffs = []
    for col in numeric_cols:
        diff = (df_run[col] - df_ver[col]).values.astype(float)
        avg_sig = _running_avg(diff, time_arr, tau)
        peak_run = float(np.nanmax(np.abs(df_run[col].values)))
        peak_ver = float(np.nanmax(np.abs(df_ver[col].values)))
        peak = max(peak_run, peak_ver, 0.0)
        threshold = tol + rtol * peak
        peak_avg = float(np.max(np.abs(avg_sig)))
        if peak_avg <= threshold:
            continue
        first_idx = int(np.argmax(np.abs(avg_sig) > threshold))
        diffs.append({
            'param': col,
            'peak_avg': peak_avg,
            'mean_avg': float(np.mean(np.abs(avg_sig))),
            'first_time': float(time_arr[first_idx]),
            'avg_series': avg_sig,
            'threshold': threshold,
        })

    return {
        'file': run_path.name,
        'ver_file': ver_path.name,
        'n_rows': n,
        'diffs': sorted(diffs, key=lambda d: d['peak_avg'], reverse=True),
        'df_run': df_run,
        'df_ver': df_ver,
        'time': time_arr,
        'tau': tau,
    }


def report_rms(results, tol, rtol, tau):
    """Print a table of parameters whose EWMA difference is significant."""
    any_diff = any(r.get('diffs') for r in results)
    print(f"\n{'=' * 72}")
    print(f"  CompareRunRun EWMA  |  tol={tol}  rtol={rtol}  tau={tau}s  |  {len(results)} pair(s)")
    print(f"{'=' * 72}\n")
    for r in results:
        run_file = r['file']
        ver_file = r.get('ver_file', '')
        pair_label = f"{run_file}  vs  {ver_file}"
        if 'error' in r:
            print(f"  {pair_label}")
            print(f"    ERROR: {r['error']}\n")
            continue
        if not r['diffs']:
            print(f"  {pair_label}  — no EWMA differences > tol={tol}+rtol={rtol}*peak"
                  f"  ({r['n_rows']} rows,  tau={tau}s)\n")
            continue
        print(f"  {pair_label}  ({r['n_rows']} rows, {len(r['diffs'])} differing param(s),  tau={tau}s)")
        print(f"    {'param':<30}  {'peak|avg|':>12}  {'mean|avg|':>12}  {'first_t':>10}")
        print(f"    {'-' * 30}  {'-' * 12}  {'-' * 12}  {'-' * 10}")
        for d in r['diffs']:
            print(f"    {d['param']:<30}  {d['peak_avg']:>12.6f}"
                  f"  {d['mean_avg']:>12.6f}  {d['first_time']:>10.3f}")
        print()
    if not any_diff:
        print("  All pairs agree within tolerance.\n")


_RMS_COLS = 3
_RMS_ROWS = 3
_RMS_PER_FIG = _RMS_COLS * _RMS_ROWS


def plot_rms_diffs(results, data_file=None, save_plots=False, show_killer_=True, hardcopy=False):
    """Plot the EWMA difference curve for every significant parameter.

    Each subplot shows ewma(run - test) vs time.  Dashed ±threshold lines
    mark the significance boundary so the viewer can see how far each
    parameter drifts.  Only parameters that exceeded the threshold appear.
    When show_killer_=False returns (fig_list, fig_files, save_pdf_path).
    """
    fig_list = []
    fig_files = []
    save_pdf_path = None

    for r in results:
        if 'error' in r or not r.get('diffs'):
            continue

        run_file = r['file']
        ver_file = r.get('ver_file', '')
        diffs = r['diffs']
        time_arr = r['time']
        tau = r.get('tau', 60.0)

        version = version_from_data_file(data_file) if data_file else 'no_name'
        _, save_pdf_path, _ = local_paths(version)
        n_figs = math.ceil(len(diffs) / _RMS_PER_FIG)

        for fig_idx in range(n_figs):
            batch = diffs[fig_idx * _RMS_PER_FIG:(fig_idx + 1) * _RMS_PER_FIG]
            n_sub = len(batch)
            n_rows = math.ceil(n_sub / _RMS_COLS)
            fig, axes = plt.subplots(n_rows, _RMS_COLS,
                                     figsize=(5 * _RMS_COLS, 3 * n_rows), squeeze=False)
            fig_list.append(fig)
            fig_label = f"  [{fig_idx + 1}/{n_figs}]" if n_figs > 1 else ""
            fig.suptitle(f"EWMA diff  τ={tau}s\n{run_file}  vs  {ver_file}{fig_label}",
                         fontsize=8)

            for sub_idx, d in enumerate(batch):
                ax = axes[sub_idx // _RMS_COLS][sub_idx % _RMS_COLS]
                thr = d['threshold']
                ax.axhline(0.0,    color='gray',   linewidth=0.6, linestyle='-')
                ax.axhline( thr,   color='salmon',  linewidth=0.8, linestyle='--')
                ax.axhline(-thr,   color='salmon',  linewidth=0.8, linestyle='--')
                ax.plot(time_arr, d['avg_series'], linewidth=1)
                ax.set_title(f"{d['param']}\npeak={d['peak_avg']:.4g}  thr=±{thr:.3g}",
                             fontsize=8)
                ax.set_xlabel('time (s)', fontsize=7)
                ax.tick_params(labelsize=7)
                ax.grid(True, linewidth=0.4)

            for empty_idx in range(n_sub, n_rows * _RMS_COLS):
                axes[empty_idx // _RMS_COLS][empty_idx % _RMS_COLS].set_visible(False)
            fig.tight_layout(rect=(0, 0, 1, 0.93))

            fig_file_name = os.path.join(save_pdf_path,
                                         f'CompareRunRun_ewma_{len(fig_list)}.png')
            fig_files.append(fig_file_name)
            if save_plots:
                plt.savefig(fig_file_name, format='png')

    if not fig_list:
        return ([], [], save_pdf_path) if not show_killer_ else None

    plt.show(block=False)

    if not show_killer_:
        return fig_list, fig_files, save_pdf_path

    string = 'plots ' + str(fig_list[0].number) + ' - ' + str(fig_list[-1].number)
    show_killer(string, 'CompareRunRun', fig_list=fig_list, fig_files=fig_files,
                pdf_path=save_pdf_path,
                pdf_base=os.path.join(save_pdf_path, 'CompareRunRun_ewma'),
                hardcopy=hardcopy)


# ── main comparison function ──────────────────────────────────────────────────

# noinspection PyPep8Naming
def compare_run_run(keys=None, data_file_folder_run=None, data_file_folder_test=None, sync_to_ctime=False,
                    terse=True, hardcopy=False):

    print(f"\ncompare_run_run:\n{keys=}\n{data_file_folder_run=}\n{data_file_folder_test=}\n{sync_to_ctime=}\n{terse=}\n{hardcopy=}\n")

    date_time = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    # date_ = datetime.now().strftime("%y%m%d")

    # Transient  inputs
    zero_zero = False
    time_end = None

    # Regression suite
    data_file_txt_run = keys[0][0]
    unit_key_run = keys[0][1]
    data_file_txt_test = keys[1][0]
    unit_key_test = keys[1][1]

    # Folder operations
    version = version_from_data_path(data_file_folder_test)
    _, save_pdf_path, _ = local_paths(version)

    # Load old ref data
    data_file_run = str(PurePosixPath(data_file_folder_run) / data_file_txt_run)
    mon_run, sim_run, f_run, data_file_run_clean, temp_flt_file_run_clean, sync_info_run = \
        load_data(data_file_run, 1, unit_key_run, zero_zero, time_end)
    sim_s_run = None
    mon_run.str_ = 'r1'
    sim_run.str_ = 's1'
    f_run.str_ = 'f1'

    # Load new test data
    data_file_test = str(PurePosixPath(data_file_folder_test) / data_file_txt_test)
    mon_test, sim_test, f_test, data_file_ver_clean, temp_flt_file_ver_clean, sync_info_test = \
        load_data(data_file_test, 1, unit_key_test, zero_zero, time_end)
    sim_s_test = None
    mon_test.str_ = 'r2'
    sim_test.str_ = 's2'
    f_test.str_ = 'f2'

    # Synchronize
    # Time since beginning of data to sync pulses
    if not sync_info_run.is_empty and not sync_info_test.is_empty and \
            sync_info_run.length == sync_info_test.length and (sync_info_run.length > 0 or sync_to_ctime is True):
        # Make target sync vector
        master_sync_del = calculate_master_sync(sync_info_run.del_mon, sync_info_test.del_mon)
        sync_info_run.synchronize(master_sync_del)
        mon_run.time = sync_info_run.time_mon.copy()
        sync_info_test.synchronize(master_sync_del)
        mon_test.time = sync_info_test.time_mon.copy()
        # print(f"{sync_to_ctime=}\n{sync_info_run.del_mon=}\n{sync_info_test.del_mon=}\n{master_sync_del=}\n{mon_test.time=}")
    elif sync_to_ctime:
        cTime_0_run = mon_run.cTime[0]
        cTime_sync = cTime_0_run
        mon_run.time = mon_run.cTime - cTime_sync
        mon_test.time = mon_test.cTime - cTime_sync
    else:
        print(f"Using simplified sync with |Ib|>0.  Data sets too small to sync or not equivalent number of sync pulses")

    # Plots
    fig_list = []
    fig_files = []
    dir_root_run, data_root_run = str(PurePosixPath(data_file_run_clean).parent), PurePosixPath(data_file_run_clean).name
    data_root_run = data_root_run.replace('.csv', '')
    dir_root_test, data_root_test = str(PurePosixPath(data_file_ver_clean).parent), PurePosixPath(data_file_ver_clean).name
    data_root_test = data_root_test.replace('.csv', '')

    filename = data_root_run + '__' + data_root_test + '_' + PurePosixPath( Path(__file__).as_posix()).stem
    filename = str(PurePosixPath(save_pdf_path) / filename)
    plot_title = dir_root_run + '/' + data_root_run + '__' + dir_root_test + '/' + data_root_test + '   ' + date_time

    S = PlotOptions(terse=terse, save_plots=hardcopy)

    if not S.terse:
        if temp_flt_file_run_clean and len(f_run.time_ux) > 1:
            fig_list, fig_files = over_fault(f_run, filename, fig_files=fig_files, plot_title=plot_title, subtitle='faults',
                                             fig_list=fig_list, save_plots=S.save_plots)

        if temp_flt_file_ver_clean and len(f_test.time_ux) > 1:
            fig_list, fig_files = over_fault(f_test, filename, fig_files=fig_files, plot_title=plot_title, subtitle='faults',
                                             fig_list=fig_list, save_plots=S.save_plots)

    fig_list, fig_files = dom_plot(mon_run, mon_test, sim_run, sim_test, sim_s_run, sim_s_test, filename, fig_files,
                                   plot_title=plot_title, fig_list=fig_list, run_type='RunRun', terse=S.terse,
                                   save_plots=S.save_plots)  # all over all

    # Numeric run-vs-run EWMA comparison.
    # compare_run_sim saves struct CSVs as  {clean_stem}_{struct}.csv  in the
    # temp folder, e.g. data_file_run_clean stem + '_sim_run.csv'.
    try:
        _tol = 1e-3
        _rtol = 1e-3
        _tau = 960.0  # EWMA time constant in seconds — tune to suppress timing jitter
        _run_stem  = Path(data_file_run_clean).stem   if data_file_run_clean else None
        _test_stem = Path(data_file_ver_clean).stem   if data_file_ver_clean else None
        _run_temp  = Path(data_file_run_clean).parent if data_file_run_clean else None
        _test_temp = Path(data_file_ver_clean).parent if data_file_ver_clean else None
        print(f"\ncompare_run_run EWMA step:"
              f"\n  run  stem={_run_stem}  temp={_run_temp}"
              f"\n  test stem={_test_stem}  temp={_test_temp}")
        _ewma_pairs = []
        for _suffix in ('_mon_run.csv', '_sim_run.csv'):
            if not (_run_stem and _test_stem and _run_temp and _test_temp):
                break
            _rf = _run_temp  / (_run_stem  + _suffix)
            _tf = _test_temp / (_test_stem + _suffix)
            _r_ok = _rf.is_file()
            _t_ok = _tf.is_file()
            print(f"  {_suffix[1:-4]:12s}  run={_rf.name}  exists={_r_ok}  test={_tf.name}  exists={_t_ok}")
            if _r_ok and _t_ok:
                _ewma_pairs.append((_rf, _tf))
        print()
        if _ewma_pairs:
            _rr_results = [compare_pair_rms(r, v, _tol, _rtol, _tau) for r, v in _ewma_pairs]
            report_rms(_rr_results, _tol, _rtol, _tau)
            _rr_ret = plot_rms_diffs(_rr_results, data_file=data_file_test,
                                     save_plots=S.save_plots, show_killer_=False,
                                     hardcopy=hardcopy)
            if _rr_ret:
                _rr_figs, _rr_files, _ = _rr_ret
                fig_list.extend(_rr_figs)
                fig_files.extend(_rr_files)
        else:
            print("  compare_run_run EWMA: no clean data files available")
    except Exception as _rr_e:
        print(f"compare_run_run EWMA step ERROR: {_rr_e}")
        traceback.print_exc()

    print('showing plots...')
    plt.ion()
    plt.show(block=False)

    string = 'plots ' + str(fig_list[0].number) + ' - ' + str(fig_list[-1].number)
    show_killer(string, 'CompareRunRun', fig_list=fig_list, fig_files=fig_files, pdf_path=save_pdf_path, pdf_base=filename, hardcopy=hardcopy)
    cleanup_fig_files(fig_files)
    print('DONE')

    return fig_list, fig_files


# noinspection PyUnusedLocal
def main():
    import sys
    if sys.platform == 'linux':
        gdrive = '/home/daveg/gdrive/'
    else:
        gdrive = 'G:/My Drive/'

    # Cut-pasted from GUI_TestSOC Run window
    keys = [('rapidTweakRegression_soc3p2_hi_lo_bb.csv', 'g20260524_soc3p2_hi_lo_bb'),
            ('rapidTweakRegression_soc3p2_hi_lo_bb.csv', 'g20260524a_soc3p2_hi_lo_bb')]
    data_file_folder_run = 'G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20260524'
    data_file_folder_test = 'G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20260524a'
    sync_to_ctime = False
    terse = True
    hardcopy = True

    compare_run_run(keys=keys, data_file_folder_run=data_file_folder_run, data_file_folder_test=data_file_folder_test,
                    sync_to_ctime=sync_to_ctime, terse=terse, hardcopy=hardcopy)


if __name__ == '__main__':  # Example usage.  Ran ok 20260217
    main()
