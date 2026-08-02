# CompareRunHistMain: drive a CompareRunHist case
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

"""Executive to drive a CompareRunHist case."""
from CompareRunHist import compare_run_hist


# noinspection PyPep8Naming
def main():  # Example usage: ok 20260217
    # Cut-pasted from GUI_TestSOC Run window
    data_file = "G:/My Drive/GitHubArchive/SOC_Particle/dataReduction\\g20250612a\\ampHiEmptFail_soc3p2_hi_lo_bb.csv"
    unit_key = "g20250612a_soc3p2_hi_lo_bb"
    time_end = None
    plots = True
    strict_overplot = True
    terse = True
    dt_resample = 10
    Tb_force = None
    use_mon_soc = False
    verbose = True
    request_history_run_sim = None
    request_history_hist_sim = None

    compare_run_hist(
        data_file=data_file,
        unit_key=unit_key,
        plots=plots,
        time_end=time_end,
        use_mon_soc=use_mon_soc,
        verbose=verbose,
        strict_overplot=strict_overplot,
        terse=terse,
        dt_resample=dt_resample,
        Tb_force=Tb_force,
        request_history_run_sim=request_history_run_sim,
        request_history_hist_sim=request_history_hist_sim,
    )


if __name__ == "__main__":  # Example usage.  Ran ok 202602xx
    main()
