# MonSimClasses:  Subclasses used to support replicate()
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

from Battery import calculate_capacity
from Battery import Battery as Battery
from filter.KF1x1 import KF1x1VarDtxx
import numpy.lib.recfunctions as rfn
from filter.myFilters import LagExp
from pyDAGx import myTables
import Globals as G
import numpy as np


class ProArray:
    def __init__(self, data, mutable=False):
        # Initialize a NumPy array, marked as "internal" with a leading underscore
        if not isinstance(data, (list, np.ndarray)):
            raise TypeError("Data must be a list or NumPy array.")
        if not mutable:
            self._data = np.array(data)
        else:
            self._data = data

    @property
    def data(self):
        """
        Getter for the array data. Returns a copy to prevent external modification
        of the internal array.
        """
        return self._data.copy()

    def __getitem__(self, index=None):
        return self._data[max(min(index, len(self._data) - 1), 0)]

    def __setitem__(self, index, value):
        self._data[index] = value
        return None

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return f"ProArray({self._data})"


class SensorLooparound:
    """Collect Looparound sense parameters to create proper delays in data feed and connections to model"""

    def __init__(self, ib, ib_dyn, e_wrap_trim, e_wrap_filt):
        self.ib = ib
        self.ib_init = self.ib[0]
        self.ib_dyn = ib_dyn
        self.e_wrap_trim = e_wrap_trim
        self.e_wrap_filt = e_wrap_filt

    def update(self, i):
        self.ib_init = self.ib[max(i - 1, 0)]


# noinspection PyPep8Naming
class Sensors:
    """Collect various sense parameters to create proper delays in data feed and connections to model"""

    def __init__(self, OPT, rp, run_type=None):
        self.run_type = run_type
        if self.run_type == "HistSim":
            self.mon_run = OPT.mon_run.copy()
            self.sim_run = OPT.sim_run.copy()
        else:
            self.mon_run = OPT.mon_run
            self.sim_run = OPT.sim_run
        if self.run_type == "RunSim":
            if hasattr(self.mon_run, "mtb") and self.mon_run.mtb is not None:
                self.mod_tb = self.mon_run.mtb
            else:
                self.mod_tb = np.copy(self.mon_run.mod_data)
            self.Tb = self.mon_run.Tb[0]
            self.Tb_f = self.mon_run.Tb_f[0]
            self.lut_dTb = None
            self.dTb = 0.0
            self.Tb_f_rate = self.mon_run.Tb_f_rate[0]
            self.Tb_past = self.mon_run.Tb[0] + self.dTb
            self.Tb_f_past = self.mon_run.Tb_f[0] + self.dTb
            self.Tb_f_rate_past = self.mon_run.Tb_f_rate[0]
            self.TbSenseFilt = LagExp(0, Battery.TB_FILT, Battery.TB_HDWE_MIN, Battery.TB_HDWE_MAX)
            self.TbModelFilt = LagExp(0, Battery.TB_FILT, Battery.TB_HDWE_MIN, Battery.TB_HDWE_MAX)
            self.WrapLoopAmp = SensorLooparound(
                self.mon_run.ib_amp_hdwe, self.mon_run.ib_dyn_m, self.mon_run.e_wrap_m_trim, self.mon_run.e_wrap_m_filt
            )
            self.WrapLoopNoa = SensorLooparound(
                self.mon_run.ib_noa_hdwe, self.mon_run.ib_dyn_n, self.mon_run.e_wrap_n_trim, self.mon_run.e_wrap_n_filt
            )
            self.Battery = Battery
            if hasattr(self.mon_run, "vovcm"):
                pos_m_init = self.mon_run.vovcmkf[0] if hasattr(self.mon_run, "vovcmkf") else self.mon_run.vovcm[0]
                self.KfShuntAmp = KF1x1VarDtxx(
                    initial_position=pos_m_init,
                    initial_velocity=self.mon_run.kf_v_m[0],
                    dt=0.1,
                    proc_noise_std=Battery.KF_Q_STD,
                    meas_noise_std=Battery.KF_R_STD,
                )
                if hasattr(self.mon_run, "P00m"):
                    self.KfShuntAmp.P = np.array([[self.mon_run.P00m[0], self.mon_run.P01m[0]], [self.mon_run.P10m[0], self.mon_run.P11m[0]]])
                    self.KfShuntAmp.P_prior = self.KfShuntAmp.P.copy()
            if hasattr(self.mon_run, "vovcn") and self.mon_run.vovcn is not None:
                # print(f"input:   KF_Q_STD {self.Battery.KF_Q_STD}  KF_R_STD {self.Battery.KF_R_STD}")
                self.Battery.KF_Q_STD /= 1.0
                self.Battery.KF_R_STD /= 1.0
                # print(f"using:   KF_Q_STD {self.Battery.KF_Q_STD}  KF_R_STD {self.Battery.KF_R_STD}")
                pos_n_init = self.mon_run.vovcnkf[0] if hasattr(self.mon_run, "vovcnkf") else self.mon_run.vovcn[0]
                self.KfShuntNoa = KF1x1VarDtxx(
                    initial_position=pos_n_init,
                    initial_velocity=self.mon_run.kf_v_n[0],
                    dt=0.1,
                    proc_noise_std=self.Battery.KF_Q_STD,
                    meas_noise_std=self.Battery.KF_R_STD,
                )
                if hasattr(self.mon_run, "P00n"):
                    self.KfShuntNoa.P = np.array([[self.mon_run.P00n[0], self.mon_run.P01n[0]], [self.mon_run.P10n[0], self.mon_run.P11n[0]]])
                    self.KfShuntNoa.P_prior = self.KfShuntNoa.P.copy()

            self.ib_amp_model = self.mon_run.ib_amp_model
            if OPT.mon_run.mib[0]:
                self.ib_amp = self.mon_run.ib_amp_model[0]
                self.ib_noa = self.mon_run.ib_noa_model[0]
            else:
                self.ib_amp = self.mon_run.ib_amp_hdwe[0]
                self.ib_noa = self.mon_run.ib_noa_hdwe[0]
            self.ib_dyn = ProArray(self.mon_run.ib_dyn, mutable=True)
            self.z = self.mon_run.z
            self.ib_in_s = self.sim_run.ib_in_s
            self.ib_charge_s = self.sim_run.ib_charge_s
            self.ib_dyn_s = self.sim_run.ib_dyn_s
            self.dv_dyn_s = self.sim_run.dv_dyn_s
            self.dt_s = self.sim_run.dt_s if hasattr(self.sim_run, "dt_s") else self.mon_run.dt
            self.d_delta_q_s_init = 0.0
            self.delta_q_s_init = self.sim_run.delta_q_s[0] if hasattr(self.sim_run, "delta_q_s") and len(self.sim_run.delta_q_s) > 0 else 0.0
            self.Tb_model_f_fut = self.mon_run.Tb_model_f[1]
            self.Tb_model_f_rate_fut = self.mon_run.Tb_model_f_rate[1]
            self.e_wrap_init = self.mon_run.e_wrap[0]
            self.e_wrap_m_init = self.mon_run.e_wrap_m[0]
            self.e_wrap_n_init = self.mon_run.e_wrap_n[0]
            self.dTb = 0.0
            # self.Tb_f = self.mon_run.Tb_f
            self.ib_init = self.mon_run.ib[0]
            self.ib_charge_init = self.mon_run.ib_charge[0]
            self.vb_init = self.mon_run.vb[0]
            self.voc_stat_init = self.mon_run.voc_stat[0]
            self.ib_amp_model = self.mon_run.ib_amp_model
            self.voc_stat_f_lstate = self.mon_run.voc_stat_f_lstate
            self.voc_stat_f_lstate_init = self.voc_stat_f_lstate[0]

        elif self.run_type == "HistSim":
            if not hasattr(self.mon_run, "ib_dyn_m"):
                self.mon_run.ib_dyn_m = np.copy(self.mon_run.ib_amp_hdwe_f)
            if not hasattr(self.mon_run, "ib_dyn_n"):
                self.mon_run.ib_dyn_n = np.copy(self.mon_run.ib_noa_hdwe_f)

            self.dt_s = self.sim_run.dt_s if hasattr(self.sim_run, "dt_s") else self.mon_run.dt
            if not hasattr(self.mon_run, "ibmm"):
                self.mon_run.ibmm = np.copy(self.mon_run.ib_amp_hdwe_f)
            if not hasattr(self.mon_run, "ib_noa_model"):
                self.mon_run.ib_noa_model = np.copy(self.mon_run.ib_noa_hdwe_f)
            if not hasattr(self.mon_run, "ib_h"):
                self.mon_run.ib_h = np.copy(self.mon_run.ib_f)
            self.Battery = Battery

            if hasattr(self.mon_run, "e_wrap"):
                self.e_wrap_init = self.mon_run.e_wrap[0]
                self.e_wrap_m_init = self.mon_run.e_wrap_m[0]
                self.e_wrap_n_init = self.mon_run.e_wrap_n[0]
            else:
                self.e_wrap_init = self.mon_run.e_wrap_filt[0]
                self.e_wrap_m_init = self.mon_run.e_wrap_m_filt[0]
                self.e_wrap_n_init = self.mon_run.e_wrap_n_filt[0]
            self.e_wrap_filt_init = self.mon_run.e_wrap_filt[0]
            self.voc_stat_init = self.mon_run.voc_stat_f[0]
            self.lut_dTb = None
            self.dTb = 0.0
            self.Tb = self.mon_run.Tb_f[0]
            self.Tb_f_rate = np.copy(self.Tb_f) * 0.0
            self.Tb_past = self.mon_run.Tb_f[0] + self.dTb
            self.Tb_f_past = self.mon_run.Tb_f[0] + self.dTb
            self.Tb_f_rate_past = np.copy(self.Tb_f) * 0.0
            self.TbModelFilt = LagExp(0, Battery.TB_FILT, Battery.TB_HDWE_MIN, Battery.TB_HDWE_MAX)
            self.TbSenseFilt = LagExp(0, Battery.TB_FILT, Battery.TB_HDWE_MIN, Battery.TB_HDWE_MAX)

            self.WrapLoopAmp = SensorLooparound(
                self.mon_run.ib_amp_hdwe_f,
                self.mon_run.ib_dyn_m,
                self.mon_run.e_wrap_m_trim,
                self.mon_run.e_wrap_m_filt,
            )
            if not hasattr(self.mon_run, "e_wrap_n_trim"):  # for old config that didn't have n_trim
                self.mon_run.e_wrap_n_trim = self.mon_run.e_wrap_m_trim.copy() * 0.0
            self.WrapLoopNoa = SensorLooparound(
                self.mon_run.ib_noa_hdwe_f,
                self.mon_run.ib_dyn_n,
                self.mon_run.e_wrap_n_trim,
                self.mon_run.e_wrap_n_filt,
            )
            self.ib_amp = self.mon_run.ib_amp_hdwe_f
            self.ib_noa = self.mon_run.ib_noa_hdwe_f
            self.ib_init = self.mon_run.ib_f[0]
            self.ib_dyn = ProArray(self.mon_run.ib_dyn)
            self.ib_charge_init = self.mon_run.ib_charge_f[0]
            self.vb_init = self.mon_run.vb_f[0]
            self.ib_amp_model = self.mon_run.ib_amp_hdwe_f
            self.z = self.mon_run.z
            self.z_init = self.z[0]
            self.voc_stat_f_lstate = self.mon_run.voc_stat_f_lstate
            self.voc_stat_f_lstate_init = self.voc_stat_f_lstate[0]

        self.i = 0
        self.sat_init = self.mon_run.sat[0]
        self.soc_s = self.mon_run.soc_s
        if hasattr(self.mon_run, "Tb_model_f_fut"):
            self.Tb_model_f_fut = self.mon_run.Tb_model_f_fut[0]

        # q
        if not hasattr(self.sim_run, "qcap_s"):
            self.qcap_s = calculate_capacity(
                q_cap_rated_scaled=self.mon_run.qcrs_s,
                dqdt=self.mon_run.dqdt,
                tb_f=self.Tb_f,
                t_rated=self.mon_run.t_rated,
            )
        else:
            self.qcap_s = self.sim_run.qcap_s
        if not hasattr(self.sim_run, "delta_q_s"):
            self.delta_q_s = -self.qcap_s * (1.0 - self.mon_run.soc_s)
        else:
            self.delta_q_s = self.sim_run.delta_q_s
        self.d_delta_q_s_init = 0.0
        self.delta_q_s_init = self.delta_q_s[0]

        self.ib_in_s = self.sim_run.ib_in_s
        if not hasattr(self, "ib_dyn_s"):
            self.ib_dyn_s = np.copy(self.ib_in_s)
        self.dv_dyn_s = self.sim_run.dv_dyn_s
        self.ib_s_init = self.ib_in_s[0]
        self.ib_charge_s_init = self.ib_charge_s[0]
        self.ioc_s_init = self.ib_in_s[0]
        self.voc_s_init = self.sim_run.voc_stat_s[0]
        self.hx_init = self.mon_run.voc_soc[0]
        self.x_init = self.mon_run.soc[0]
        self.x_prior_init = self.x_init
        self.soc_ekf_init = self.mon_run.soc[0]
        self.z_init = self.mon_run.z[0]
        self.reset_kf = True
        self.VoVcm = 0.0
        self.VoVcm_f = 0.0
        self.kf_v_m = 0.0
        self.VoVcn = 0.0
        self.VoVcn_f = 0.0
        self.kf_v_n = 0.0
        self.iscm = 0.0
        self.iscm_f = 0.0
        self.iscn = 0.0
        self.iscn_f = 0.0
        if not hasattr(self.mon_run, "Tb"):
            self.mon_run.Tb = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_f"):
            self.mon_run.Tb_f = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_f_rate"):
            self.mon_run.Tb_f_rate = 0.0 * self.mon_run.Tb_h_f.copy()
        if not hasattr(self.mon_run, "Tb_model"):
            self.mon_run.Tb_model = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_model_f_fut"):
            if hasattr(self.mon_run, "Tb_h_f"):
                self.mon_run.Tb_model_f_fut = self.mon_run.Tb_h_f
            else:
                self.Tb_model_f_fut = self.mon_run.Tb_f[0]
        if not hasattr(self.mon_run, "Tb_model_f"):
            self.mon_run.Tb_model_f = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_hdwe"):
            self.mon_run.Tb_hdwe = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_hdwe_f"):
            self.mon_run.Tb_hdwe_f = self.mon_run.Tb_h_f
        if not hasattr(self.mon_run, "Tb_hdwe_f_rate"):
            self.mon_run.Tb_hdwe_f_rate = 0.0 * self.mon_run.Tb_h_f.copy()
        if hasattr(self.sim_run, "Tb_f_s"):
            pass
        else:
            self.sim_run.Tb_f_s = self.mon_run.Tb_f
        if hasattr(self.mon_run, "mtb"):
            self.mtb = self.mon_run.mtb[0]
        else:
            self.mtb = rp.modeling_Tb

    def __str__(self, prefix=""):
        s = prefix + "TFDelay:\n"
        return s

    # noinspection PyPep8Naming
    def assign_tb(self, mon_Tb, mon_Tb_f, mon_Tb_f_rate):
        self.Tb = mon_Tb + self.dTb
        self.Tb_f = mon_Tb_f + self.dTb
        self.Tb_f_rate = mon_Tb_f_rate

    def calc_temp_pass_1(self, OPT, mon_, sim_, i, rp, dt=None, reset=None):
        mon = mon_
        sim = sim_
        if dt is not None:
            mon.dt = dt
            sim.dt = dt
        curr_reset = reset if reset is not None else mon.reset
        if OPT.run_type == "RunSim":
            self.Tb_model_f_rate_fut = OPT.mon_run.Tb_model_f_rate[i]
        else:
            self.Tb_model_f_rate_fut = OPT.mon_run.Tb_model_f_rate_fut[i]
        if hasattr(OPT.mon_run, "Tb_hdwe"):
            mon.Tb_hdwe = OPT.mon_run.Tb_hdwe[i]
        else:
            mon.Tb_hdwe = OPT.mon_run.Tb_f[i]
        if hasattr(OPT.mon_run, "Tb_model"):
            mon.Tb_model = OPT.mon_run.Tb_model[i]
        else:
            mon.Tb_model = OPT.mon_run.Tb_f[i]
        mon.reset_temp = (i < 2) or curr_reset or OPT.run_type == "HistSim"  # make sure temp init is longer than reset
        mon.dt_temp = mon.dt
        if OPT.run_type == "RunSim":
            if bool(self.mod_tb[i]):
                mon.Tb = OPT.mon_run.Tb[i]
            else:
                mon.Tb = mon.Tb_hdwe  # past value
            mon.Tb_s = mon.Tb
            sim.Tb_f = self.Tb_f
        else:
            sim.Tb = OPT.mon_run.Tb_f[i]
            mon.Tb = OPT.mon_run.Tb_f[i]
            mon.Tb_s = OPT.mon_run.Tb_f[i]
            sim.Tb_f = self.Tb_f_past  # same model and hdwe
        if i > 0:
            self.update_tb()
            if self.mtb:
                mon.Tb = self.Tb_past
                mon.Tb_f = self.Tb_f_past
                mon.Tb_f_rate = self.Tb_f_rate_past
            else:
                mon.Tb = self.Tb
                mon.Tb_f = self.Tb_f
                mon.Tb_f_rate = self.Tb_f_rate

        return mon, sim

    def calc_temp_pass_2(self, mon_run, mon, Battery_, rp, i=None, dt=None, reset=None):
        if dt is not None:
            mon.dt = dt
        # else:
        #     if not rp.modeling_ib:
        #         mon.dt = mon_run.dt[i]  # hardware mode: present frame
        #     else:
        #         mon.dt = dt_val if dt_val > 0.0 else mon_run.dt[i]  # model mode: present frame
        self.temp_load_and_filter(mon_run, mon, Battery_, rp, i, reset=reset)
        self.select_temp(mon_run, mon, Battery_, rp, i, reset=reset)
        self.assign_tb(mon.Tb, mon.Tb_f, mon.Tb_f_rate)
        return mon

    def select_temp(self, mon_run, mon, Battery_, rp, i=None, reset=None):
        # select_temp
        mon.Tb_flt = bool(mon_run.Tb_flt[i]) if hasattr(mon_run, "Tb_flt") else False
        mon.Tb_fa = bool(mon_run.Tb_fa[i]) if hasattr(mon_run, "Tb_fa") else False
        if rp.modeling_Tb:
            if mon.Tb_fa:
                mon.Tb = Battery.NOMINAL_TB
                mon.Tb_f = Battery.NOMINAL_TB
                mon.Tb_f_rate = 0.0
            elif mon.Tb_flt:  # lgv
                pass
            else:
                mon.Tb = mon.Tb_model
                mon.Tb_f = mon.Tb_model_f
                mon.Tb_f_rate = mon.Tb_model_f_rate
            mon.Tb_rstate = self.TbModelFilt.rstate
            mon.Tb_state = self.TbModelFilt.state
        else:
            if mon.Tb_fa:
                mon.Tb = Battery.NOMINAL_TB
                mon.Tb_f = Battery.NOMINAL_TB
                mon.Tb_f_rate = 0.0
            else:
                mon.Tb = mon.Tb_hdwe
                mon.Tb_f = mon.Tb_hdwe_f
                mon.Tb_f_rate = mon.Tb_hdwe_f_rate
            mon.Tb_rstate = self.TbSenseFilt.rstate
            mon.Tb_state = self.TbSenseFilt.state
        # Final assignments
        if not mon.reset_temp:
            mon.Tb = self.Tb_past
            mon.Tb_f_rate = mon.Tb_model_f_rate

    def temp_load_and_filter(self, mon_run, mon, Battery_, rp, i, reset=None):
        curr_reset = reset if reset is not None else mon.reset
        dt_earlier = mon_run.dt[i] if hasattr(mon_run, "dt") else mon.dt
        if hasattr(mon_run, "Tb_hdwe_f"):
            mon.Tb_hdwe_f = self.TbSenseFilt.calculate_tau_seeded(
                mon.Tb_hdwe,
                mon_run.Tb_hdwe_f[i],
                curr_reset or mon.Tb_fa,
                dt_earlier,
                Battery_.TB_FILT,
                rmax=Battery_.T_RLIM,
                rmin=-Battery_.T_RLIM,
            )
        mon.Tb_hdwe_f_rate = self.TbSenseFilt.rate
        mon.Tb_hdwe_f_dt = self.TbSenseFilt.dt
        mon.Tb_hdwe_f_tau = self.TbSenseFilt.tau
        mon.Tb_hdwe_f_rstate = self.TbSenseFilt.rstate
        mon.Tb_hdwe_f_lstate = self.TbSenseFilt.state

        if hasattr(mon_run, "Tb_model_f"):
            if rp.modeling_Tb:
                mon.Tb_model_f = self.TbModelFilt.calculate_tau_seeded(
                    mon.Tb_model,
                    mon_run.Tb_model_f[i],
                    curr_reset or mon.Tb_fa,
                    dt_earlier,
                    # <--- Applied here
                    Battery_.TB_FILT,
                    rmax=Battery_.T_RLIM,
                    rmin=-Battery_.T_RLIM,
                )
            else:
                mon.Tb_model_f = self.Tb_model_f_fut
                mon.Tb_model_f_rate = self.Tb_model_f_rate_fut
                self.Tb_model_f_fut = self.TbModelFilt.calculate_tau_seeded(
                    mon.Tb_model,
                    mon_run.Tb_model_f[i],
                    curr_reset or mon.Tb_fa,
                    dt_earlier,
                    # <--- AND applied here in the else branch!
                    Battery_.TB_FILT,
                    rmax=Battery_.T_RLIM,
                    rmin=-Battery_.T_RLIM,
                )
        else:
            mon.Tb_model_f = self.Tb_model_f_fut
            mon.Tb_model_f_rate = self.Tb_model_f_rate_fut
            mon.Tb_model_f = self.TbModelFilt.calculate_tau_seeded(
                mon.Tb_model,
                mon.Tb_model,
                curr_reset or mon.Tb_fa,
                dt_earlier,
                # <--- AND applied here!
                Battery_.TB_FILT,
                rmax=Battery_.T_RLIM,
                rmin=-Battery_.T_RLIM,
            )
        mon.Tb_model_f_rate = self.TbModelFilt.rate
        mon.Tb_model_f_dt = self.TbModelFilt.dt
        mon.Tb_model_f_rstate = self.TbModelFilt.rstate
        mon.Tb_model_f_lstate = self.TbModelFilt.state

    def update_ekf(self, i_ekf):
        self.z_init = self.z[i_ekf]
        self.voc_stat_f_lstate_init = self.voc_stat_f_lstate[i_ekf]

    def update(self, i):
        self.i = min(max(i, 0), len(self.mon_run.time) - 1)

    def update_ib_vb(self, i):
        self.i = min(max(i, 0), len(self.mon_run.time) - 1)
        self.WrapLoopAmp.update(i)
        self.WrapLoopNoa.update(i)

        if hasattr(self.mon_run, "kfres") and self.mon_run.kfres is not None:
            self.reset_kf = bool(self.mon_run.kfres[i])
            if hasattr(self.mon_run, "vovcm"):
                self.VoVcm = self.mon_run.vovcm[i]
                dt_m = self.mon_run.dtm[i] if hasattr(self.mon_run, "dtm") else self.mon_run.ib_dyn_T_m[i]
                self.KfShuntAmp.calculate(reset=self.reset_kf, dt=dt_m, in_=self.VoVcm)
                self.VoVcm_f, self.kf_v_m = self.KfShuntAmp.get_state()
                self.VoVcm_f = float(self.VoVcm_f)
                self.kf_v_m = float(self.kf_v_m)
            self.VoVcn = self.mon_run.vovcn[i]
            dt_n = self.mon_run.dtn[i] if hasattr(self.mon_run, "dtn") else self.mon_run.ib_dyn_T_n[i]
            self.KfShuntNoa.calculate(reset=self.reset_kf, dt=dt_n, in_=self.VoVcn)
            self.VoVcn_f, self.kf_v_n = self.KfShuntNoa.get_state()
            self.VoVcn_f = float(self.VoVcn_f)
            self.kf_v_n = float(self.kf_v_n)
            if hasattr(self.mon_run, "vovcm"):
                self.iscm = float((self.VoVcm * Battery.SHUNT_AMP_GAIN) / Battery.NP)
                self.iscm_f = float((self.VoVcm_f * Battery.SHUNT_AMP_GAIN) / Battery.NP)
            else:
                self.iscm = 0.0
                self.iscm_f = 0.0
            self.iscn = float((self.VoVcn * Battery.SHUNT_NOA_GAIN) / Battery.NP)
            self.iscn_f = float((self.VoVcn_f * Battery.SHUNT_NOA_GAIN) / Battery.NP)

    def update_tb(self):
        self.Tb_past = self.Tb
        self.Tb_f_past = self.Tb_f
        self.Tb_f_rate_past = self.Tb_f_rate
