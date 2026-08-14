# battery_constants.py - Battery class-level constant declarations
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

"""Mixin class holding all Battery class-level constant declarations.
All attributes are initialized to None and populated at runtime by the
configuration loader, except NOM_UNIT_CAP which has a fixed default."""

import numpy as np


class BatteryConstants:
    AMP_WRAP_TRIM_GAIN = None
    ap_cc_diff_slr = None
    ap_dc_dc_on = None # Truck charging
    ap_disab_ib_fa = None
    ap_disab_tb_fa = None
    ap_disab_vb_fa_lt = None
    ap_ds_voc_soc = None
    ap_dv_voc_soc = None
    ap_eframe_mult = None
    ap_ewhi_slr = None
    ap_ewlo_slr = None
    ap_hys_scale = None
    ap_h_alpha = None
    ap_h_max = None
    ap_ib_diff_slr = None
    ap_ib_quiet_slr = None
    ap_nS = None
    cp_ts = None
    CHEM = None
    DF2 = None
    EKF_CONV = None
    EKF_NOM_DT = None
    EKF_Q_SD_NORM = None
    EKF_R_SD_NORM = None
    EKF_T_CONV = None
    EKF_T_RES = None
    EWHI_SLR = None
    EWHI_TRM_SLR = None
    EWLO_SLR = None
    EWLO_TRM_SLR = None
    F_MAX_T_WRAP = None
    HDB_VB = None
    H_MAX = None
    H_ALPHA = 0.05
    hdwe_ib_hi_lo = None
    HDWE_IB_HI_LO_AMP_HI = None
    HDWE_IB_HI_LO_AMP_LO = None
    HDWE_IB_HI_LO_NOA_HI = None
    HDWE_IB_HI_LO_NOA_LO = None
    HYS_IB_THR = None
    HYS_SOC_MIN_MARG = None
    IB_ABS_MAX_AMP = None
    IB_ABS_MAX_NOA = None
    IB_DIFF_SLR = None
    IB_LO_ACTIVE_SET = None
    IB_LO_ACTIVE_RES = None
    IB_MIN_UP = None
    IBATT_DISAGREE_RES = None
    IBATT_DISAGREE_THRESH = None
    IBATT_INST_DIFF_RES = None
    IBATT_INST_DIFF_SET = None
    IMAX_NUM = None
    KF_Q_STD = None
    KF_R_STD = None
    MAX_TRIM_RATE = None
    MAX_WRAP_ERR_FILT = None
    MAX_Y_FILT = None
    MIN_Y_FILT = None
    MXEPS = None
    NOA_WRAP_TRIM_GAIN = None
    NOMINAL_TB = None
    NOMINAL_VB = None
    NP = None
    NS = None
    RATED_TEMP = None
    SHUNT_AMP_GAIN = None
    SHUNT_NOA_GAIN = None
    skip_battery = None
    sp_cutback_gain_slr = None
    sp_Dw = None
    sp_ib_disch_slr = None
    sp_ib_disch_slr_z = None
    sp_s_cap_mon = None
    sp_s_cap_sim = None
    sp_vsat_add = None
    T_RLIM = None
    TAU_ERR_FILT = None
    TAU_Y_FILT = None
    TB_FILT = None
    TB_MAX = None
    TB_MIN = None
    TB_HDWE_MAX = None
    TB_HDWE_MIN = None
    TCHARGE_DISPLAY_DEADBAND = None
    TMAX_FILT = None
    VB_DC_DC = None
    VB_MAX = None
    VB_MIN = None
    VOC_STAT_FILT = None
    WN_Y_FILT = None
    WRAP_ERR_FILT = None
    WRAP_HI_AMPV = None
    WRAP_LO_AMPV = None
    WRAP_HI_NOAV = None
    WRAP_LO_NOAV = None
    WRAP_HI_RES = None
    WRAP_HI_SET = None
    WRAP_HI_SETAT_MARG = None
    WRAP_HI_SETAT_SLR = None
    WRAP_LO_RES = None
    WRAP_LO_SET = None
    IBATT_DISAGREE_SET = None
    WRAP_MOD_C_RATE = None
    WRAP_SOC_HI_OFF = None
    WRAP_SOC_HI_SLR = None
    WRAP_SOC_LO_OFF_ABS = None
    WRAP_SOC_LO_OFF_REL = None
    WRAP_SOC_LO_SLR = None
    WRAP_SOC_MOD_OFF = None
    ZETA_Y_FILT = None
    D_SOC_S = 0.0  # Bias on soc to voc-soc lookup to simulate error in estimation, esp cold battery near 0 C
    NOM_UNIT_CAP =  108.4
    ap_nP = 1.
    TEMP_DELAY_MS = 0.6


# noinspection PyPep8Naming
def load_off_nominal_battery(Battery_to_add=None):
    # Load off-nominal Battery values.  Load Battery
    if Battery_to_add is not None:
        # Scroll through all off-nominals make dictionary
        Battery_off_dict = {}
        for field_name in Battery_to_add.dtype.names:
            # print(f"field_name {field_name}  ", end='')
            try:
                Battery_off_dict[field_name] = Battery_to_add[field_name][0]  # Use first entry only.  Discard the rest
            except IndexError:
                Battery_off_dict[field_name] = Battery_to_add[field_name]
        return Battery_off_dict
    else:
        return None


# noinspection PyPep8Naming
def apply_off_nominal_battery(Battery_, Battery_off_dict):
    print(f"Battery dictionary from firmware to applied to python Battery class")
    if Battery_off_dict:
        # Check exist
        for key in Battery_off_dict:
            if not np.isnan(Battery_off_dict[key]):
                if not key.startswith("__") and key in dir(Battery_):
                    # print(f"Battery.{key} = {getattr(Battery_, key)} to be replaced")
                    pass
                else:
                    print(f"{key} MISSING  *****************")
                    # exit(1)
        # Make translation
        for key in dir(Battery_):
            if key in Battery_off_dict and not key.startswith("__"):
                val = Battery_off_dict[key]
                if key == "TEMP_DELAY_MS" and val > 10.0:
                    val /= 1000.0
                setattr(Battery_, key, val)
