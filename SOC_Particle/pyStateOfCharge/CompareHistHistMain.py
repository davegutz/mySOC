# CompareHistHistMain: drive a CompareHistHist case
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

"""Executive to drive a CompareHistHist case."""
from CompareHistHist import compare_hist_hist


def main():
    # User inputs (multiple input_files allowed)

    # Cut-pasted from GUI_TestSOC Run window
    data_file_run = "G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20250612a/ampHiEmptFail_soc2p2_hi_lo_bb.csv"
    unit_key_run = "g20250612a_soc2p2_hi_lo_bb"
    data_file_tst = "G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20250612a/ampHiEmptFail_soc3p2_hi_lo_bb.csv"
    unit_key_tst = "g20250612a_soc3p2_hi_lo_bb"
    dt_resample = 1
    terse = True
    hardcopy = False

    compare_hist_hist(
        data_file_run=data_file_run,
        unit_key_run=unit_key_run,
        data_file_tst=data_file_tst,
        unit_key_tst=unit_key_tst,
        dt_resample=dt_resample,
        terse=terse,
        hardcopy=hardcopy,
    )


if __name__ == "__main__":  # Example usage.  Ran ok 20260217
    main()
