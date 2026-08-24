# CompareRunSimMain:  drive a CompareRunSim case
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

"""Executive to drive a CompareRunSim case."""
import CompareRunSim
from CompareRunSim import compare_run_sim
import sys

# noinspection PyUnusedLocal
def main():  # Example usage.  ok on 20260217
    CompareRunSim.COMPARE_RUN_SIM_MAIN_RUNNING = True
    try:
        if sys.platform == "linux":
            gdrive = "/home/daveg/gdrive/"
        else:
            gdrive = "G:/My Drive/"

        # Cut-pasted from GUI_TestSOC Run window
        """Request history:
            1:  ekf
            2:  soc
            3:  soc_s
            4:  temp
            5:  volt all
            6:  kf
            7:  dyn_m
            8:  vb_wrap
            9:  dyn_n
            10: cc_diff
        """
        data_file = '/home/daveg/.local/SOC_Particle/dataReduction/g20260612a/stepUp_soc3p2_hi_lo_bb.csv'
        unit_key = 'g20260612a_soc3p2_hi_lo_bb'
        time_end = None
        compare_run_ver = True
        shift_soc_s = True
        plots = True
        use_mon_soc_ = False
        verbose = False
        scale_batt = 1.0
        slr_hys_sim = 1.0
        request_history = 11
        init_time = None
        time_shift = None
        strict_overplot = True
        terse = True
        hardcopy = False
        mon_str = ''

        compare_run_sim(
            data_file=data_file,
            unit_key=unit_key,
            plots=plots,
            time_end=time_end,
            use_mon_soc_=use_mon_soc_,
            verbose=verbose,
            scale_batt=scale_batt,
            slr_hys_sim=slr_hys_sim,
            request_history=request_history,
            init_time=init_time,
            time_shift=time_shift,
            strict_overplot=strict_overplot,
            terse=terse,
            hardcopy=hardcopy,
            compare_run_ver=compare_run_ver,
            shift_soc_s=shift_soc_s,
        )
    finally:
        CompareRunSim.COMPARE_RUN_SIM_MAIN_RUNNING = False

if __name__ == "__main__":  #
    main()
