# Faults - Battery monitory circuit fault detection logic
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
# type: ignore
# noinspection
# PyAttributeOutsideInit, PyUnresolvedReferences, PyPep8Naming, PyShadowingNames, PyShadowingBuiltins,
# PyUnboundLocalVariable, PyUnfilledParameters
# pylint: disable=invalid-name, no-member, attribute-defined-outside-init, redefined-outer-name, redefined-builtin,
# used-before-assignment

"""Define fault logic for Battery charge monitoring circuits"""


from filter.TFDelay import TFDelay
from filter.myFilters import LagExp, TustinIntegrator


# noinspection PyPep8Naming
class Diff:
    """Compare predicted voltage to actual and track toward zero to eliminate biases"""

    def __init__(self, dt=0.1):
        from Battery import Battery

        self.reset = True
        self.dt = dt
        self.ib_amp = 0.
        self.ib_noa = 0.
        self.ib_lo_limited_hi = False
        self.ib_lo_limited_lo = False
        self.ib_diff = 0.0
        self.ib_diff_f = self.ib_diff
        self.ib_noa_hi = False
        self.ib_noa_lo = False
        self.ib_amp_hi = False
        self.ib_amp_lo = False
        self.disable_amp_fault = False
        self.ib_diff_thr = 0.
        self.ib_diff_hi_flt = False
        self.ib_diff_lo_flt = False
        self.ib_diff_hi_fa = False
        self.ib_diff_lo_fa = False
        self.IbDiffFilt = LagExp(
            dt=self.dt,
            tau=Battery.TAU_ERR_FILT,
            min_=-Battery.IBATT_DISAGREE_THRESH * 1.5,
            max_=Battery.IBATT_DISAGREE_THRESH * 1.5)
        self.ib_diff_T = 0.
        self.ib_diff_rstate = 0.
        self.ib_diff_state = 0.
        self.ib_diff_tau = 0.
        self.LoHi = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
        )
        self.IbdHiPer = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IBATT_DISAGREE_SET,
            t_false=Battery.IBATT_DISAGREE_RES,
        )
        self.IbdLoPer = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IBATT_DISAGREE_SET,
            t_false=Battery.IBATT_DISAGREE_RES,
        )
        self.IbdPosPer = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IBATT_INST_DIFF_SET,
            t_false=Battery.IBATT_INST_DIFF_RES,
        )
        self.IbdNegPer = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IBATT_INST_DIFF_SET,
            t_false=Battery.IBATT_INST_DIFF_RES,
        )
        self.LoLo = TFDelay(
            dt=self.dt,
            in_=False,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
        )

    # Update the loop
    # needs to be called twice with reset=True to initialize properly
    def calculate(self, reset=True, dt=None, ib_amp=None, ib_noa=None):
        from Battery import Battery

        self.reset = reset
        self.dt = dt
        self.ib_amp = ib_amp
        self.ib_noa = ib_noa

        self.ib_amp_hi = self.ib_amp >= Battery.HDWE_IB_HI_LO_AMP_HI / Battery.NP
        self.ib_lo_limited_hi = self.LoHi.calculate(
            in_=self.ib_amp_hi,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
            dt=self.dt,
            reset=self.reset,
        )  # non-latching
        self.ib_amp_lo = self.ib_amp <= Battery.HDWE_IB_HI_LO_AMP_LO / Battery.NP
        self.ib_lo_limited_lo = self.LoLo.calculate(
            in_=self.ib_amp_lo,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
            dt=self.dt,
            reset=self.reset,
        )  # non-latching

        # Match C++ Fault::ib_logic(): disable when both sensors simultaneously at same limit
        self.ib_noa_hi = self.ib_noa >= Battery.HDWE_IB_HI_LO_NOA_HI / Battery.NP
        self.ib_noa_lo = self.ib_noa <= Battery.HDWE_IB_HI_LO_NOA_LO / Battery.NP
        self.disable_amp_fault = (self.ib_amp_hi and self.ib_noa_hi) or (self.ib_amp_lo and self.ib_noa_lo)

        self.ib_diff = self.ib_amp - self.ib_noa
        if self.ib_lo_limited_hi:
            self.ib_diff = max(0.0, self.ib_diff)
        elif self.ib_lo_limited_lo:
            self.ib_diff = min(0.0, self.ib_diff)
        self.ib_diff_f = self.IbDiffFilt.calculate(in_=self.ib_diff,
                    reset=self.reset or self.disable_amp_fault or self.ib_lo_limited_hi or self.ib_lo_limited_lo,
                    dt=self.dt)
        self.ib_diff_T = self.IbDiffFilt.dt
        self.ib_diff_rstate = self.IbDiffFilt.rstate
        self.ib_diff_state = self.IbDiffFilt.state
        self.ib_diff_tau = self.IbDiffFilt.tau
        self.ib_diff_thr = Battery.IBATT_DISAGREE_THRESH * Battery.ap_ib_diff_slr
        self.ib_diff_hi_flt = self.IbdPosPer.calculate(self.ib_diff_f >= self.ib_diff_thr,
                                                  Battery.IBATT_INST_DIFF_SET, Battery.IBATT_INST_DIFF_RES,
                                                  self.dt, self.reset)
        self.ib_diff_lo_flt = self.IbdNegPer.calculate(self.ib_diff_f <= -self.ib_diff_thr,
                                                  Battery.IBATT_INST_DIFF_SET, Battery.IBATT_INST_DIFF_RES,
                                                  self.dt, self.reset)
        self.ib_diff_hi_fa = self.IbdHiPer.calculate(self.ib_diff_hi_flt,
                                                  Battery.IBATT_DISAGREE_SET, Battery.IBATT_DISAGREE_RES,
                                                  self.dt, self.reset)
        self.ib_diff_lo_fa = self.IbdLoPer.calculate(self.ib_diff_lo_flt,
                                                  Battery.IBATT_DISAGREE_SET, Battery.IBATT_DISAGREE_RES,
                                                  self.dt, self.reset)
        return self.ib_diff


# noinspection PyPep8Naming
class Looparound:
    """Compare predicted voltage to actual and track toward zero to eliminate biases"""

    def __init__(self, Mon_, wrap_hi_volt=0.0, wrap_lo_volt=0.0, max_err=None,
                 name=""):
        from Battery import Battery

        self.Mon = Mon_
        self.reset = True
        self.dt = 0.0
        self.dt_past = 0.0
        self.dv_dyn = 0.0
        self.e_wrap = 0.0
        self.e_wrap_filt = 0.0
        self.e_wrap_rate = 0.0
        self.ib_dyn = 0.0
        self.wrap_hi_volt = wrap_hi_volt
        self.wrap_lo_volt = wrap_lo_volt
        self.e_wrap_trim = 0.0
        self.e_wrap_trimmed = 0.0
        self.hi_fail = False
        self.hi_fault = False
        self.lo_fail = False
        self.lo_fault = False
        self.chem = Mon_.chemistry
        self.ChargeTransfer = LagExp(
            dt=Battery.EKF_NOM_DT,
            max_=Battery.NOM_UNIT_CAP * self.Mon.scale_cap,
            min_=-Battery.NOM_UNIT_CAP * self.Mon.scale_cap,
            tau=self.chem.tau_ct,
        )
        self.ewhi_thr = 0.0
        self.ewhi_thr_base = 0.0
        self.ewlo_thr = 0.0
        self.ewlo_thr_base = 0.0
        self.ib = 0.0
        self.ib_past = 0.0
        self.ib_past2 = 0.0
        self.Trim = TustinIntegrator(dt=2.0, min_=-max_err * 10.0, max_=max_err * 10.0)
        self.vb = 0.0
        self.voc = 0.0
        self.voc_soc = 0.0
        self.WrapErrFilt = LagExp(dt=2.0, min_=-max_err, max_=max_err, tau=Battery.WRAP_ERR_FILT)
        self.WrapHi = TFDelay(dt=2.0, in_=False, t_true=Battery.WRAP_HI_SET, t_false=Battery.WRAP_HI_RES)
        self.WrapLo = TFDelay(dt=2.0, in_=False, t_true=Battery.WRAP_LO_SET, t_false=Battery.WRAP_LO_RES)
        self.name = name

    # Update the loop
    # needs to be called twice with reset=True to initialize properly
    def calculate(
        self,
        reset=True,
        rp=None,
        ib=0.0,
        loop_gain=0.0,
        dt=None,
        ewsat_slr=1.0,
        ewmin_slr=1.0,
        ib_dyn_init=0.0,
        e_wrap_filt_init=0.0,
        e_wrap_trim_init=0.0,
        freeze=False,
    ):
        from Battery import Battery

        frozen = 1.0 - float(freeze)
        self.reset = reset
        self.dt = dt
        self.ib = ib
        self.vb = self.Mon.vb_past
        self.voc_soc = self.Mon.voc_soc
        if rp.modeling_vb or rp.modeling_ib:
            dt_into_ct = self.dt_past
            dt_into_wrap = self.dt_past
            ib_into_ct = self.ib_past2
        else:
            dt_into_ct = self.dt
            dt_into_wrap = self.dt
            ib_into_ct = self.ib_past

        self.ib_dyn = self.ChargeTransfer.calculate_tau_seeded(
            ib_into_ct, ib_dyn_init, self.reset, dt_into_ct, self.chem.tau_ct, text=self.name
        )
        # print(f"{reset=} {ib=} {self.ib=} {self.ib_past=} {self.ChargeTransfer.rstate=}")
        self.dv_dyn = self.ib_dyn * self.chem.r_ct + ib_into_ct * self.chem.r_0
        self.voc = self.vb - self.dv_dyn
        self.e_wrap = self.voc_soc - self.voc

        # Trimmer using past values
        trim_rate_lim = max(min(self.e_wrap_filt * loop_gain, Battery.MAX_TRIM_RATE), -Battery.MAX_TRIM_RATE)
        self.e_wrap_trim = -self.Trim.calculate_lim(
            in_=trim_rate_lim * frozen,
            dt=min(dt_into_wrap, Battery.F_MAX_T_WRAP),
            reset=self.reset,
            init_value=-e_wrap_trim_init,
            max_=-self.ewlo_thr_base * Battery.EWLO_TRM_SLR,
            min_=-self.ewhi_thr_base * Battery.EWHI_TRM_SLR,
        )
        self.e_wrap_trimmed = self.e_wrap + self.e_wrap_trim
        e_wrap_filt_rate = 1e300
        if freeze:
            e_wrap_filt_rate = 0.0
        self.e_wrap_filt = self.WrapErrFilt.calculate_seeded(
            in_=self.e_wrap_trimmed,
            _out_init=e_wrap_filt_init,
            reset=self.reset,
            dt=dt_into_wrap,
            text=self.name,
            rmin=-e_wrap_filt_rate,
            rmax=e_wrap_filt_rate,
        )
        self.e_wrap_rate = self.WrapErrFilt.rate

        # Thresholds. Scalars are calculated by Flt->wrap_scalars()
        self.ewhi_thr_base = self.wrap_hi_volt * Battery.ap_ewhi_slr
        self.ewhi_thr = self.ewhi_thr_base * ewsat_slr * ewmin_slr
        self.ewlo_thr_base = self.wrap_lo_volt * Battery.ap_ewlo_slr
        self.ewlo_thr = self.ewlo_thr_base * ewsat_slr * ewmin_slr

        # sat logic screens out voc jump when ib>0 when saturated
        # wrap_hi and wrap_lo don't latch because need them available to check next ib sensor selection for dual ib
        # sensor
        # wrap_vb latches because vb is single sensor  faultAssign( (e_wrap_filt_ >= ewhi_thr_ && !Mon->sat()),
        # WRAP_HI_FLT);

        self.hi_fault = self.e_wrap_filt >= self.ewhi_thr
        self.hi_fail = self.WrapHi.calculate(
            in_=self.hi_fault,
            t_true=Battery.WRAP_HI_SET,
            t_false=Battery.WRAP_HI_RES,
            dt=dt_into_wrap,
            reset=self.reset,
        )  # non-latching
        self.lo_fault = self.e_wrap_filt <= self.ewlo_thr
        self.lo_fail = self.WrapLo.calculate(
            in_=self.lo_fault,
            t_true=Battery.WRAP_LO_SET,
            t_false=Battery.WRAP_LO_RES,
            dt=dt_into_wrap,
            reset=self.reset,
        )  # non-latching
        self.ib_past2 = self.ib_past
        self.ib_past = self.ib
        self.dt_past = self.dt


# noinspection PyPep8Naming
class MyLooparounds:
    """Instantiate two Looparound objects (Amp and Noa) and their parameters."""

    def __init__(self, Mon_):
        from Battery import Battery

        self.LoopIbAmp = Looparound(
            Mon_=Mon_,
            wrap_hi_volt=Battery.WRAP_HI_AMPV,
            wrap_lo_volt=Battery.WRAP_LO_AMPV,
            max_err=Battery.MAX_WRAP_ERR_FILT / (Battery.IB_ABS_MAX_NOA / Battery.IB_ABS_MAX_AMP),
            name="Amp",
        )
        self.LoopIbNoa = Looparound(
            Mon_=Mon_,
            wrap_hi_volt=Battery.WRAP_HI_NOAV,
            wrap_lo_volt=Battery.WRAP_LO_NOAV,
            max_err=Battery.MAX_WRAP_ERR_FILT,
            name="Noa",
        )

        # Amp (m) parameters
        self.ib_dyn_m = 0.0
        self.ib_dyn_T_m = 0.0
        self.ib_dyn_rstate_m = 0.0
        self.ib_dyn_lstate_m = 0.0
        self.ib_dyn_tau_m = 0.0
        self.dv_dyn_m = 0.0
        self.voc_m = 0.0
        self.voc_soc_m = 0.0
        self.ib_wrp_T_m = 0.0
        self.ib_wrp_tau_m = 0.0
        self.ib_wrp_state_m = 0.0
        self.ib_wrp_rate_m = 0.0
        self.ib_wrp_reset_m = 0.0
        self.e_wrap_m = None
        self.e_wrap_m_filt = None
        self.e_wrap_m_trim = None
        self.e_wrap_m_trimmed = 0.0
        self.e_wrap_m_rate = None
        self.ewmhi_thr = 0.0
        self.ewmlo_thr = 0.0
        self.wrap_hi_m_flt = False
        self.wrap_hi_m_fa = False
        self.wrap_lo_m_flt = False
        self.wrap_lo_m_fa = False

        # Noa (n) parameters
        self.ib_dyn_n = 0.0
        self.ib_dyn_T_n = 0.0
        self.ib_dyn_rstate_n = 0.0
        self.ib_dyn_lstate_n = 0.0
        self.ib_dyn_tau_n = 0.0
        self.dv_dyn_n = 0.0
        self.ib_wrp_T_n = 0.0
        self.ib_wrp_tau_n = 0.0
        self.ib_wrp_state_n = 0.0
        self.ib_wrp_rate_n = 0.0
        self.e_wrap_n = None
        self.e_wrap_n_filt = None
        self.e_wrap_n_trim = None
        self.e_wrap_n_trimmed = 0.0
        self.e_wrap_n_rate = None
        self.ewnhi_thr = 0.0
        self.ewnlo_thr = 0.0
        self.wrap_hi_n_flt = False
        self.wrap_hi_n_fa = False
        self.wrap_lo_n_flt = False
        self.wrap_lo_n_fa = False


# noinspection PyPep8Naming
class Wrap(MyLooparounds):
    """Wrap error detection and current channel scaling logic"""

    def __init__(self, Mon_):
        from Battery import Battery
        from filter.Scale import ScaleSelector
        from filter.myFilters import SlidingDeadband
        from filter.TFDelay import TFDelay

        MyLooparounds.__init__(self, Mon_)

        self.sdb_voc = SlidingDeadband(Battery.HDB_VB)
        self.e_wrap = 0.0
        self.e_wrap_filt = 0.0
        self.e_wrap_rate = 0.0
        self.ib_amp_pst = 0.0
        self.ib_noa_pst = 0.0
        self.ib_noa_2pst = 0.0
        self.e_wrap_m_reset = True
        self.sel_brk_hdwe = ScaleSelector(
            Battery.HDWE_IB_HI_LO_NOA_LO,
            Battery.HDWE_IB_HI_LO_AMP_LO,
            Battery.HDWE_IB_HI_LO_AMP_HI,
            Battery.HDWE_IB_HI_LO_NOA_HI,
        )
        self.ib_lo_active = True
        self.IbLoLimitedLo = TFDelay(
            in_=False,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
            dt=0.1,
        )
        self.IbLoLimitedHi = TFDelay(
            in_=False,
            t_true=Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
            t_false=Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
            dt=0.1,
        )


    def calculate(
        self, reset=True, ib_noa_hdwe=0.0, SN=None, ib_amp=0.0, ib_noa=0.0, ib_amp_pst=None,
            ib_noa_pst=None, rp=None
    ):
        """Wrap logic"""
        from Battery import Battery
        import Globals as G

        dt_local = self.dt

        # e_wrap scalars normally calculated in Sensors
        if self.soc >= Battery.WRAP_SOC_HI_OFF:
            ewsat_slr = Battery.WRAP_SOC_HI_SLR
            ewmin_slr = 1.0
        elif self.soc <= max(self.soc_min + Battery.WRAP_SOC_LO_OFF_REL, Battery.WRAP_SOC_LO_OFF_ABS):
            ewsat_slr = 1.0
            ewmin_slr = Battery.WRAP_SOC_LO_SLR

        elif self.voc_soc > (self.vsat - Battery.WRAP_HI_SETAT_MARG) or (
            (self.voc_stat > (self.vsat - Battery.WRAP_HI_SETAT_MARG))
            and (self.ib / Battery.NOM_UNIT_CAP > Battery.WRAP_MOD_C_RATE)
            and (self.soc > Battery.WRAP_SOC_MOD_OFF)
        ):
            ewsat_slr = Battery.WRAP_HI_SETAT_SLR
            ewmin_slr = 1.0
        else:
            ewsat_slr = 1.0
            ewmin_slr = 1.0

        # Individual wrap logic
        if ib_noa is not None:
            if rp.modeling_vb or rp.modeling_ib or SN.run_type == "HistSim":
                self.ib_noa = ib_noa
                self.ib_noa_pst = ib_noa_pst
                dt_local = self.dt
                ibnoa = self.ib_noa
            else:
                self.ib_noa = ib_noa
                self.ib_noa_pst = ib_noa_pst
                dt_local = self.dt_past
                ibnoa = self.ib_noa
            self.LoopIbNoa.calculate(
                reset=reset,
                rp=rp,
                ib=ibnoa,
                loop_gain=Battery.NOA_WRAP_TRIM_GAIN,
                dt=dt_local,
                ewmin_slr=ewmin_slr,
                ewsat_slr=ewsat_slr,
                ib_dyn_init=SN.WrapLoopNoa.ib_dyn[G.i],
                e_wrap_filt_init=SN.mon_run.e_wrap_n_filt[G.i],
                e_wrap_trim_init=SN.mon_run.e_wrap_n_trim[G.i],
                freeze=False,
            )
        if ib_amp is not None:
            if rp.modeling_vb or rp.modeling_ib or SN.run_type == "HistSim":
                self.ib_amp = ib_amp
                self.ib_amp_pst = ib_amp_pst
                ibamp = self.ib_amp
            else:
                self.ib_amp = ib_amp
                self.ib_amp_pst = ib_amp_pst
                ibamp = self.ib_amp
            self.ib_amp_hi = self.ib_amp >= Battery.HDWE_IB_HI_LO_AMP_HI / Battery.ap_nP
            self.ib_amp_lo = self.ib_amp <= Battery.HDWE_IB_HI_LO_AMP_LO / Battery.ap_nP
            self.ib_noa_hi = self.ib_noa >= Battery.HDWE_IB_HI_LO_NOA_HI / Battery.ap_nP
            self.ib_noa_lo = self.ib_noa <= Battery.HDWE_IB_HI_LO_NOA_LO / Battery.ap_nP
            self.ib_lo_limited_lo = self.IbLoLimitedLo.calculate(
                self.ib_amp_lo,
                Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
                Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
                dt=dt_local,
                reset=self.e_wrap_m_reset,
            )
            self.ib_lo_limited_hi = self.IbLoLimitedHi.calculate(
                self.ib_amp_hi,
                Battery.IB_LO_ACTIVE_SET * Battery.cp_ts,
                Battery.IB_LO_ACTIVE_RES * Battery.cp_ts,
                dt=dt_local,
                reset=self.e_wrap_m_reset,
            )
            self.ib_lo_active = not self.ib_lo_limited_hi and not self.ib_lo_limited_lo
            self.disable_amp_fault = (self.ib_amp_hi and self.ib_noa_hi) or (self.ib_amp_lo and self.ib_noa_lo)
            self.e_wrap_m_reset = reset
            self.LoopIbAmp.calculate(
                reset=self.e_wrap_m_reset,
                rp=rp,
                ib=ibamp,
                loop_gain=Battery.AMP_WRAP_TRIM_GAIN,
                dt=dt_local,
                ewmin_slr=ewmin_slr,
                ewsat_slr=ewsat_slr,
                ib_dyn_init=SN.WrapLoopAmp.ib_dyn[G.i],
                e_wrap_filt_init=SN.mon_run.e_wrap_m_filt[G.i],
                e_wrap_trim_init=SN.mon_run.e_wrap_m_trim[G.i],
                freeze=not self.ib_lo_active,
            )

        # Scale for final selection
        e_wrap_m_val = self.LoopIbAmp.e_wrap
        e_wrap_n_val = self.LoopIbNoa.e_wrap
        e_wrap_m_filt_val = self.LoopIbAmp.e_wrap_filt
        e_wrap_n_filt_val = self.LoopIbNoa.e_wrap_filt
        e_wrap_m_rate_val = self.LoopIbAmp.e_wrap_rate
        e_wrap_n_rate_val = self.LoopIbNoa.e_wrap_rate

        self.e_wrap = self.sel_brk_hdwe.scale_select(ib_noa_hdwe, e_wrap_m_val, e_wrap_n_val)
        self.e_wrap_filt = self.sel_brk_hdwe.scale_select(ib_noa_hdwe, e_wrap_m_filt_val, e_wrap_n_filt_val)
        self.e_wrap_rate = self.sel_brk_hdwe.scale_select(ib_noa_hdwe, e_wrap_m_rate_val, e_wrap_n_rate_val)

    # Maintain wrap() method alias
    wrap = calculate

