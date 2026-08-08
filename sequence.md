  Top Level Minor Frame

```c++
// Definitions
PHOTON_ADC_VOLT = 3.3        // Photon ADC range, V (3.3)
PHOTON_ADC_COUNT = 4096      // Photon ADC range, counts (4096)
VB_SENSE_R_HI = 22000  // Vb high sense resistor, ohm (22000)
VB_SENSE_R_LO = 4700  // Vb low sense resistor, ohm (4700)
AMP_FILT_TAU =   4.0;  // seconds lag for Vb filtering
TB_FILT = 120.;  // seconds lag for Tb filtering
READ_DELAY = 100;   // ms minor frame update
SHUNT_AMP_R1 = 1500.  // Internal amp resistance 196x, ohms (1500)
SHUNT_AMP_R2 = 332000.  // Internal amp resistance 196x, ohms (332000)
SHUNT_NOA_R1 = 1500.  // Internal amp resistance 29.4x, ohms (1500)
SHUNT_NOA_R2 = 33200.  // Internal amp resistance 29.4x, ohms (33200)
N_LO = -11. // Fully NOA signal disch transition, A (-11)
A_LO = -10. // Fully AMP signal disch transition, A (-10)
A_HI = 10. // Fully AMP signal charge transition, A (10)
N_HI = 11. // Fully NOA signal charge transition, A (11)
D11 = V op-amp Noa pin
D13 = V op-amp Amp pin
D14 = V common Amp pin
SHUNT_GAIN = 1333.;  // Shunt V2A gain, A/V (1333 is 100A/0.075V)
NOMINAL_TB = 15.;  // Middle of the road Tb for decent reversionary, C operation, deg C (15.)
T_SAT = 24; // Saturation debounce time, sec 
T_DESAT = 20;  // De-saturation debounce time, sec
sat_cutback_gain_ = 1000.;  // Gain to retard ib when soc approaches 1, dimensionless
coul_eff_ = 0.9985;  // Coulombic efficiency - the fraction of charging 
			// input that gets turned into usable Coulombs
sat_ib_null_ = 0.;  // Current cutback value for soc=1, A

chem_ = {... }  // structure of chemical properties
sp = class SavedPars;     // Stored/retained settings & configuration flags
ap = class VolatilePars;  // Adjustment parameters (e.g. nP parallel, nS series cells)    
cp = class CommandPars;   // Control & command state flags



SHUNT_AMP_GAIN = SHUNT_GAIN * SHUNT_AMP_R1 / SHUNT_AMP_R2;
SHUNT_NOA_GAIN = SHUNT_GAIN * SHUNT_NOA_R1 / SHUNT_NOA_R2;
VO_CONV_GAIN = PHOTON_ADC_VOLT) / PHOTON_ADC_COUNT;
VH3V3_CONV_GAIN = PHOTON_ADC_VOLT) / PHOTON_ADC_COUNT;
VB_CONV_GAIN = PHOTON_ADC_VOLT) / PHOTON_ADC_COUNT) *
			((VB_SENSE_R_HI + VB_SENSE_R_LO) / VB_SENSE_R_LO);

/*
                  ^ scale
                  |
------            |          -------> 1.0 ==> all lg
       -          |        -
         -        |      -
      |    -------------          --> 0.0 ==> all sm

      |    |      |     |    |
   N_LO   A_LO    |   A_HI   N_HI
                  |
                  |
                  v
*/
// Scale select between a large ranging signal and small ranging signal for
// the same sensor.  Small might be a high precision, amplified circuit and
// large might be low precision, lightly amplified circuit
sel_brk_hdwe = new ScaleBrk( N_LO,  	A_LO,  A_HI,	N_HI);
	ScaleBrk::scale_select = {...}  // Calculation function 

user_input = model_signal_spec;
Sen = class Sensor;
Mon = class BatteryMonitor;
Sim = class BatterySim;
loop() {
read = wait_for_update(READ_DELAY);
if (read) {
	// Signal generator
	mod_add = signal_generator(user_input);

 	// Read sensors, model signals, select between them, synthesize injection
  	sense_synth_select(...) {
		load_ib_vb_tb(){
			// ib load-----------------------------------
			// Sample Ib
																	// Model temporal
			Sen->ShuntAmp->sample(...) {
				sample_Vo(){			
					sample_time_z_ = sample_time_;  						// Feedback -> PV source
					sample_time_ = millis(){								// FV source
						return system_clock_ms;
					}
		 		 	Vo_read_->analogReadDebounced(...){					// FV source
						Vo_raw_ = analogRead(D13);
					}
		  			Vo_ = float(Vo_raw_) * VO_CONV_GAIN;					// FV
		  		}
		  		sample_Vc(){
		  			Vc_read_->analogReadDebounced(...){					// FV source
							Vc_raw_ = analogRead(D14);
					}
		    			Vc_ = float(Vc_raw_) * VH3V3_CONV_GAIN;				// FV
		  		}
		  		sample_combine(){
					Vo_Vc_ = Vo_ - Vc_;									// FV
		  		}
			} // Sen->ShuntAmp->sample(...)

		 	Sen->ShuntNoAmp->sample(...){								// FV source
				// ...similar to  ShuntAmp
					Vo_raw_ = analogRead(D11);
			}
			Sen->ShuntAmp->convert(...){
				vshunt_ = Vo_Vc_;										// FV
				Ishunt_cal_ = vshunt_ * SHUNT_AMP_GAIN ;					// FV
			}
			Sen->ShuntNoAmp->convert(...){
				// ...similar to  ShuntAmp
			}
			Sen->Flt->vc_check(...);  // OS fault check
			Sen->shunt_select_initial(...){
  				Ib_amp_model_ = mod_add;								// FV
				Ib_noa_model_ = mod_add;								// FV

				Ib_amp_hdwe_ = ShuntAmp->Ishunt_cal(){					// FV
					  return Ishunt_cal_ ;
				}
  				Ib_noa_hdwe_ = ShuntNoAmp->Ishunt_cal(){					// FV
					// ... similar to ShuntAmp
				}
			}
			// Assign Ib
			if (!sp.mod_ib()) {
				// When running normally the model tracks hdwe
				Ib_model_in_ = Ib_hdwe_;  								// tbd
			} 
			// Otherwise it generates signals for feedback into monitor
			// Noise is actually separate for each signal. Simplified here
			else {
				Ib_noise = psuedo_random_binary_noise(bits=7, seed=...);		// n/a
				Ib_model_in_ = mod_add + Ib_noise;						// FV
			}

			// vb load-----------------------------------
			Sen->vb_load(myPins->Vb_pin, ...){
				Vb_raw_ = Vb_read_...;									// FV source
				...
  				Vb_hdwe_ = Vb_raw_) * VB_CONV_GAIN;						// FV
				// Note: T_ in following is UBC (past value) from previous frame
				Vb_hdwe_f_ = VbHdweFilt->calculate(..., AMP_FILT_TAU, T_, ...);	// FV
			}
			Sen->Flt->vb_check(...);										// FV

			// Tb load-----------------------------------
			Sen->Tb_load(myPins->VTb_pin, ...){
				Tb_raw_ = Tb_read_ ...;									// FV	source
				...
				Tb_hdwe_ = thermistor_equation(Tb_raw_);					// FV
				Tb_hdwe_f_ = TbHdweFilt->calculate(..., TB_FILT, T_, ...);		// FV
				...
				Tb_model_ = NOMINAL_TB + Tb_noise();						// FV
				Tb_model_f_ = TbModelFilt->calculate(..., TB_FILT, T_, ...);		// FV
				...
			}
			Sen->Flt->Tb_check(...);  //--> TB_FLT, TB_FA						// FV
		}  // load_ib_vb_tb

		// Sim initialize as needed from memory
  		if (reset_temp) {
			initialize_all(Mon, Sen, 0., false);
		}
		Sen->Sim->apply_delta_q_t(reset);
		Sen->Sim->init_battery_sim(reset, Sen);
		Mon->init_battery_mon(reset, Sen);

		// Sim calculation
		Sen->Vb_model(Sen->Sim->calculate()){
			// Inputs
  			Tb_ = Sen->Tb();											// FV
 			Tb_f_ = Sen->Tb_f();										// FV
			dt_in_ = (sample_time_ - sample_time_z_) / 1000.;					// FV
			ib_in_ = Sen->Ib_model_in() / ap.nP();							// FV
			dt_ = dt_fut_;												// Feedback --> PV source
			ib_ = ib_fut_;												// Feedback --> PV source
			Sen->Ib_model( ib_fut_ );
  
 			 // VOC-OCV model
			voc_stat_ = calc_soc_voc(soc_, Tb_f_, ...);						// Feedback --> PV source


			// ChargeTransfer dynamic model for model
			ib_dyn_ = ChargeTransfer_->calculate(ib_, reset, chem_.tau_ct, dt_);	// PV
			dvdyn_ =  ib_dyn_ * chem_.r_ct  + ib_ * chem_.r_0;				// PV
			vb_ = voc_ + dvdyn_;										// PV
			voc_soc_ = voc_stat_;										// PV

  			// Saturation logic, both full and empty
			// Pass along current to charge unless bms_off
			float ib_charge_fut = ib_in_;									// FV
			if ( sp.mod_ib )
				sat_ib_max_ = sat_ib_null_ + (1. - soc_)) *  sat_cutback_gain_ ;	// FV
			else
				 // Disable cutback when real world
				sat_ib_max_ = ib_charge_fut;								// FV
			ib_fut_ = min(ib_charge_fut, sat_ib_max_);  // the feedback of ib_		// FV

			dt_charge_ = dt_fut_;										// PV  ??????
			ib_charge_ = ib_fut_;  // Same time plane as volt calcs, added past value	// FV  ?????

			return vb_;
		} // Sen->Sim->calculate()

		// Fault Logic, & Selection Logic - selection status and fault reset
		Sen->Flt->ib_range();
		Sen->Flt->ib_logic();
		Sen->Flt->ib_wrap();
		Sen->Flt->ib_quiet();
		Sen->Flt->cc_diff();
		Sen->Flt->ib_diff();
		Sen->Flt->select_all_logic(){ 
			// Ib decision tables
			ib_decision_hi_lo(Sen){
   				ib_choice_ = ...;
				latch_ = ...;
				ib_decision_ = ...;
			}
		}  // select_all_logic


		// Apply Fault Logic to select signals
		Sen->select_volt_and_current_and_temp()){

			// ib select
			ib_choose_hi_lo() {   // Use the first argument and the table second
							   // argument to choose between 3rd and 4th arguments
				Ib_hdwe_ = scale_select( 		Ib_noa_hdwe_,   	sel_brk_hdwe,
											Ib_amp_hdwe_, 	Ib_noa_hdwe, ...)
				Ib_hdwe_model_ = scale_select(	Ib_noa_model_, 	sel_brk_hdwe,
											Ib_amp_model_, 	Ib_noa_model_, ...);
				sample_time_ib_hdwe_ = ShuntNoAmp->sample_time();
				dt_ib_hdwe_ = ShuntNoAmp->dt_ms();
			}

			// Tb select
			if (sp.mod_tb()) {  // Model Tb
				if (Flt->Tb_fa() ...) {
					Tb_ = NOMINAL_TB;
					Tb_f_ = NOMINAL_TB;
					sample_time_Tb_ = Sim->sample_time();
	    			} else if (Flt->Tb_flt() ...) { // last good value while flt resolved
					sample_time_Tb_ = sample_time_Tb_hdwe_;
					return;
				} else {
					Tb_ = Tb_model_;
					Tb_f_ = Tb_model_f_;
					sample_time_Tb_ = Sim->sample_time();
				}
			} else {  // Hardware Tb
				if (Flt->Tb_fa() ...) {
					Tb_ = NOMINAL_TB;
					Tb_f_ = NOMINAL_TB;
					sample_time_Tb_ = Sim->sample_time();
				} else if (Flt->Tb_flt() ...) {  // last good value while flt resolved
					sample_time_Tb_ = sample_time_Tb_hdwe_;
					return;
				} else {
					Tb_ = Tb_hdwe_;
					Tb_f_ = Tb_hdwe_f_;
					sample_time_Tb_ = sample_time_Tb_hdwe_;
				}
			}

			// vb select
			if (sp.mod_vb()) {  // Model vb
				Vb_f_ = Vb_;
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...) {
					Vb_ = Mon->vb_model_rev() * ap.nS();  // TODO: verify past value vb_model_rev here
					sample_time_vb_ = Sim->sample_time();
				} else {
					Vb_ = Vb_model_ + Vb_noise();
      					sample_time_vb_ = Sim->sample_time();
				}
			} else {
				Vb_f_ = Vb_hdwe_f_;
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...)) {
					Vb_ = Mon->vb_model_rev() * ap.nS();  // model backup
					sample_time_vb_ = Sim->sample_time();
				} else {
					Vb_ = Vb_hdwe_;
					sample_time_vb_ = sample_time_vb_hdwe_;
				}
  			}

			// ib
			if (sp.mod_ib()) {
				Ib_ = Ib_hdwe_model_;
				Ib_amp_ = Ib_amp_model_;
				Ib_noa_ = Ib_noa_model_;
				Vc_ = HALF_V3V3;
				sample_time_ib_ = Sim->sample_time();
				dt_ib_ = Sim->dt_fut_ms();
			} else {
				Ib_ = Ib_hdwe_;
				Ib_amp_ = Ib_amp_hdwe_;
				Ib_noa_ = Ib_noa_hdwe_;
				Vc_ = Vc_hdwe_;
				sample_time_ib_ = sample_time_ib_hdwe_;
				dt_ib_ = dt_ib_hdwe_;
			}
			T_ = double(dt_ib_) / 1000.;  // s
			now_ = sample_time_ib_;
			Sim->assign_times(input=double(now_) / 1000.){
				dt_fut_ = input - c_time_;
				c_time_ = input;
			}
		} // select_volt_and_current_and_temp

		// Charge calculation and memory store
		Sen->Sim->count_coulombs() {
			// Inputs
			Tb_ = Sen->Tb();
			Tb_f_ = Sen->Tb_f();

			// Saturation and re-init.   Goal is to set q_capacity and hold it so remember
			// last saturation status
			static bool reset_temp_past = reset_temp;  // needed because model called first in reset_temp path; need
											                 // to pick up latest
			if (initializing_all) reset_temp_past = true;
			if (!sp.mod_vb())  {  // Real world init sim to track Monitor SOC
				if (Mon->sat() || reset_temp_past) apply_delta_q(Mon->delta_q());
			} else {
				...
			}

			// Integration.   can go to -20%
			q_capacity_ = calculate_capacity(Tb_f_);
			d_delta_q_s_ = ib_charge_ * dt_charge_;  // Coulomb Counting uses Backard Euler Integration
			if (ib_charge_ > 0.) d_delta_q_s_ *= coul_eff_;
			if (reset_temp) {
				*sp_delta_q_ = 0.;
			}
			if (!reset_temp_past) {
				*sp_delta_q_ += d_delta_q_s_;
				*sp_delta_q_ = max(min(*sp_delta_q_, 0.), -q_capacity_ * 1.2);
			}
			q_ = q_capacity_ + *sp_delta_q_;
			// Normalize
			soc_ = q_ / q_capacity_;

			// Save and return
			reset_temp_past = reset_temp;
			return soc_;
		}  // Sen->Sim->count_coulombs

	}  // sense_synth_select

	// Calculate Ah remaining
	monitor(...) {
		Mon->calculate(Sen, reset_temp, reset_ekf){
			// Inputs
			Tb_f_ = Sen->Tb_f();
			vsat_ = calc_vsat();
			dt_ = Sen->T();
			c_time_ = Sen->c_time();
			vb_ = Sen->vb();
			ib_ = Sen->ib();

			// Table lookup
			voc_soc_ = voc_soc_tab(soc_, Tb_f_);

			// Battery management system model
			... /// --> bms_off, bms_charging, voltage_low

			// Charging
			ib_charge_ = ib_;
			float ib_charge_ekf = ib_charge_;
			if (bms_off_ && !bms_charging_ && sp.mod_vb()) ib_charge_ = 0.;
			if (bms_off_ && voltage_low_) ib_ = 0.;

			if (reset_temp) ib_past_ = ib_;

			// Dynamic emf. vb_ is stale when running with model
			float ib_dyn_in;
			if (sp.mod_vb())  ib_dyn_in = ib_past_;
			else  ib_dyn_in = ib_;
			ib_dyn_ = ChargeTransfer_->calculate(ib_dyn_in, reset_temp, chem_.tau_ct, dt_);
			float dvdyn = ib_dyn_ * chem_.r_ct + ib_dyn_in * chem_.r_0;
			voc_ = vb_ - dvdyn;
			if ((bms_off_ && voltage_low_) || Sen->Flt->vb_fa_lt()) {
				voc_ = voc_stat_ = voc_dead_ = vb_;
			}
			dv_dyn_ = vb_ - voc_;

			// Hysteresis model
			... // not used

			// voc(soc) table
			voc_stat_ = calc_soc_voc(soc_, Tb_f_, ...);
			voc_ = voc_stat_;

			// Reversionary model
			vb_model_rev_ = voc_soc_ + dv_dyn_;  // TODO:  Verify this is used next frame as past value

			// EKF 1x1
			cp.ekf_executing = false;
			if (eframe_ == 0 || reset_ekf) {
				cp.ekf_executing = true;
				static uint64_t ekf_now_past = Sen->now();
				float ddq_dt = ib_charge_ekf;

				// Freeze EKF with voltage fault or bms_off
				freeze_ekf_ = Sen->Flt->vb_fa_lt() || bms_off_;

				now_ekf_ = Sen->now();
				dt_ekf_ = float(now_ekf_ - ekf_now_past) / 1e3;
				ekf_now_past = now_ekf_;
				if (	ddq_dt > 0. && !sp.tweak_test()) ddq_dt *= coul_eff_;
				voc_stat_f_ = VocStatFilt->calculate(voc_stat_, reset_ekf || reset_temp, ap.voc_stat_filt(), dt_ekf_);
				if (reset_ekf) {
					solve_ekf(reset_ekf, reset_temp, Sen);
				}  else {
					predict_ekf(ddq_dt, freeze_ekf_);         // u = d(dq)/dt
					update_ekf(voc_stat_f_, 0., MXEPS);  // z = _f, estimated = voc_filtered =
						// hx, predicted = est past
				}
				soc_ekf_ = x();  // x = Vsoc (0-1 ideal capacitor voltage) proxy for soc
				q_ekf_ = soc_ekf_ * q_capacity_;
				delta_q_ekf_ = q_ekf_ - q_capacity_;
				y_ekf_ = y();  // y = z - hx, residual between measurement and predicted
				// measurement
				y_ekf_f_ = Yfilt->calculate(y_ekf_, reset_temp, dt_ekf_);

				// EKF convergence
				bool conv = abs(y_ekf_f_) < ap.ekf_conv() && !cp.soft_reset && !cp.ekf_reset;  // Initialize false
				ekf_conv_ = EKF_converged->calculate(conv, EKF_T_CONV, EKF_T_RES, ...)

				if (reset_ekf) cp.ekf_reset = false;
			}
			eframe_++;
			if (reset_temp || reset_ekf || cp.soft_reset || eframe_ >= ap.eframe_mult())
			eframe_ = 0;  // '>=' allows changing ap.eframe_mult() on the fly

			// Deadband filter
			voc_dead_ = SdVb_->update(voc_);  // used for saturation test

			// Charge time if used ekf
			tcharge_ekf = time_to_completion(soc_ekf_, ib_charge_)

			// Past value for synchronization with vb_, only when modeling
			ib_past_ = ib_;

			return vb_model_rev_;
		}  // Mon->calculate

		// Debounce saturation calculation done in ekf using voc model
		Sen->sat(Mon->is_sat(reset));
		Sen->saturated(Is_sat_delay->calculate(Sen->sat(), T_SAT, T_DESATA, ...));

		// Memory store (Count Coulombs)
		float cc_ib_in = Mon->ib_charge();
		if (Sen->Flt->ib_amp_fa() && Sen->Flt->ib_noa_fa() && !ap.fake_faults())
		cc_ib_in = 0.;
		Mon->count_coulombs(Sen, reset_temp, cc_ib_in, Sen->sat(), Sen->saturated()) {
			// Inputs
			dt_ = Sen->T();
			tb_f_ = Sen->Tb_f();
			Tb_f_ = Sen->Tb_f();
			d_delta_q_ = charge_curr * dt_;

			// State change
			double d_delta_q_inf = d_delta_q_;
			if (charge_curr > 0.) d_delta_q_ *= coul_eff_;
			sat_ = sat;
			saturated_ = saturated;

			// Saturation.   Goal is to set q_capacity and hold it so remember last saturation status.
			if (saturated_) {
				d_delta_q_ = 0.;
				*sp_delta_q_ = 0.;
			}

			// Integration.   Can go to negative
			q_capacity_ = calculate_capacity(tb_f_);
			if (!reset_temp) 
				*sp_delta_q_ = max(min(*sp_delta_q_ + d_delta_q_, 0.0), -q_capacity_ * 1.5);
			q_ = q_capacity_ + *sp_delta_q_;

			// Normalize
			soc_ = q_ / q_capacity_;

			return soc_;
		}  // Mon->count_coulombs

		// Charge charge time for display
		Mon->calc_charge_time(Mon->q(), Mon->q_capacity(), Sen->ib(), Mon->soc());
	}  // monitor

	// Print
	print_...

}  // read
}  // loop
```
