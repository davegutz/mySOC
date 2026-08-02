# CompareRunRunMain: drive a CompareRunRun case
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

"""Executive to drive a CompareRunRun case."""
import sys
from CompareRunRun import compare_run_run


# noinspection PyUnusedLocal
def main():
    if sys.platform == "linux":
        gdrive = "/home/daveg/gdrive/"
    else:
        gdrive = "G:/My Drive/"

    # Cut-pasted from GUI_TestSOC Run window
    keys = [
        ("rapidTweakRegression_soc3p2_hi_lo_bb.csv", "g20260524_soc3p2_hi_lo_bb"),
        ("rapidTweakRegression_soc3p2_hi_lo_bb.csv", "g20260524a_soc3p2_hi_lo_bb"),
    ]
    data_file_folder_run = "G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20260524"
    data_file_folder_test = "G:/My Drive/GitHubArchive/SOC_Particle/dataReduction/g20260524a"
    sync_to_c_time = False
    terse = True
    hardcopy = True

    compare_run_run(
        keys=keys,
        data_file_folder_run=data_file_folder_run,
        data_file_folder_test=data_file_folder_test,
        sync_to_c_time=sync_to_c_time,
        terse=terse,
        hardcopy=hardcopy,
    )


if __name__ == "__main__":
    main()
