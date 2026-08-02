# CompareHistSimMain: drive a CompareHistSim case
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

"""Executive to drive a CompareHistSim case."""
import sys
from CompareHistSim import compare_hist_sim


# noinspection PyUnusedLocal,PyPep8Naming
def main():  # Sample usage. OK on 20260217
    if sys.platform == "linux":
        gdrive = "/home/daveg/gdrive/"
    else:
        gdrive = "G:/My Drive/"

    # User inputs (multiple input_files allowed
    # Cut-pasted from GUI_TestSOC Run window
    # data_file = 'G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20250612a/truckHist_20260302.csv'

    data_file = "/home/daveg/.local/SOC_Particle/plink/dataReduction/g20250612a/tLoFailModel_soc3p2_hi_lo_bb.csv"
    time_end = None
    plots = False
    use_mon_csv = True
    unit_key = "g20250612a_soc3p2_hi_lo_bb"
    sync_time = None
    dt_resample = 10
    Tb_force = None
    request_history = 5
    strict_overplot = True
    terse = True
    fig_files = None
    fig_list = None
    show_killer_ = True
    hardcopy = True

    compare_hist_sim(
        data_file=data_file,
        use_mon_csv=use_mon_csv,
        unit_key=unit_key,
        dt_resample=dt_resample,
        plots=plots,
        Tb_force=Tb_force,
        request_history=request_history,
        strict_overplot=strict_overplot,
        terse=terse,
        hardcopy=hardcopy,
    )


if __name__ == "__main__":  # Example usage.  Ran ok 20260217
    main()
