//  Top Level Minor Frame

//```c++
// Definitions
PHOTON_ADC_VOLT = 3.3        // Photon ADC range, V (3.3)
PHOTON_ADC_COUNT = 4096      // Photon ADC range, counts (4096)
VB_SENSE_R_HI = 22000  // Vb high sense resistor, ohm (22000)
VB_SENSE_R_LO = 4700  // Vb low sense resistor, ohm (4700)
AMP_FILT_TAU =   4.0;  // seconds lag for Vb filteringVc
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
myPins.VTb_pin = D0  // Tb thermistor pin
myPins.Von_pin = D11  // V op-amp Noa pin
myPins.Vb_pin = D12  // Vb pin
myPins.Vom_pin = D13  // V op-amp Amp pin
myPins.Vc_pin = D14  // V op-amp common pin
SHUNT_GAIN = 1333.;  // Shunt V2A gain, A/V (1333 is 100A/0.075V)
NOMINAL_TB = 15.;  // Middle of the road Tb for decent reversionary, C operation, deg C (15.)
T_SAT = 24; // Saturation debounce time, sec 
T_DESAT = 20;  // De-saturation debounce time, sec
sat_cutback_gain_ = 1000.;  // Gain to retard ib when soc approaches 1, dimensionless
coul_eff_ = 0.9985;  // Coulombic efficiency - the fraction of charging
			// input that gets turned into usable Coulombs
sat_ib_null_ = 0.;  // Current cutback value for soc=1, A
chem_ = {... }  // structure of chemical properties
chem_.rated_temp = 25.  // Temperature at NOM_UNIT_CAP, deg C (25)
chem_.dvoc_dt = 0.004  // Change of VOC with operating temperature in range 0 - 50
                     // C V/deg C (0.004)
double Y_T[M_T] =  // Temperature breakpoints for voc table
    {5., 11.1, 20., 30., 40.};
double X_SOC[N_S] =  // soc breakpoints for voc table
    {-0.15, 0.0, 0.05, 0.10,     0.14,  0.17,   0.20,   0.25,   0.30,   0.40,   0.50,   0.60,   0.70,   0.80,   0.90,   0.99, 0.995, 1.00};
double T_VOC[M_T * N_S] =  // r(soc, dv) table  20250611 data shows this
    {	4.,    4.,        4.,       4.,    8.90, 10.40, 11.15, 11.40, 11.47, 11.60, 11.61, 11.68, 11.75, 11.81, 11.87, 11.92, 13.49, 14.45,
	4.,    4.,        4.,       4.,    8.90, 10.40, 11.15, 11.40, 11.47, 11.60, 11.61, 11.68, 11.75, 11.81, 11.87, 11.92, 13.49, 14.45
	4.,    4.,  10.00, 12.50,  12.67, 12.75, 12.79, 12.85, 12.89, 12.93, 12.94, 12.99, 13.04, 13.11, 13.15, 13.17, 13.62, 14.50,
	4.,    4.,  11.90, 12.55,  12.65, 12.70, 12.75, 12.85, 12.90, 12.98, 13.02, 13.06, 13.10, 13.14, 13.16, 13.17, 13.62, 14.50
	4.,    4.,  11.90, 12.55,  12.65, 12.70, 12.75, 12.85, 12.90, 12.98, 13.02, 13.06, 13.10, 13.14, 13.16, 13.17, 13.62, 14.50};


sp = class SavedPars;     // Stored/retained settings & configuration flags
ap = class VolatilePars;  // Adjustment parameters (e.g. nP parallel, nS series cells)    
cp = class CommandPars;   // Control & command state flags



SHUNT_AMP_GAIN = SHUNT_GAIN * SHUNT_AMP_R1 / SHUNT_AMP_R2;
SHUNT_NOA_GAIN = SHUNT_GAIN * SHUNT_NOA_R1 / SHUNT_NOA_R2;
VO_CONV_GAIN = PHOTON_ADC_VOLT / PHOTON_ADC_COUNT;
VH3V3_CONV_GAIN = PHOTON_ADC_VOLT / PHOTON_ADC_COUNT;
VB_CONV_GAIN = PHOTON_ADC_VOLT / PHOTON_ADC_COUNT *
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


// Loop
loop() {
read = wait_for_update(READ_DELAY);
if (read) {

	// Manage states
	Sen->Sim->data_of_future_passed(reset){
		...
		sample_time_s_pst_ms_ = sample_time_s_ms_;
	  soc_pst_ = soc_;
	}
	Mon->data_of_future_passed(reset){
	  soc_pst_ = soc_;
	  ...
	}

 	// Read sensors, model signals, select between them, synthesize injection
  sense_synth_select(...) {
		load_ib_vb_tb(){
			// ib load-----------------------------------
			// Sample Ib
																								// Model temporal | Hdwe temporal
			Sen->ShuntAmp->sample(...) {
				sample_Vo(){			
					sample_time_z_ms_ = sample_time_ms_;						// Feedback->PV | PV
					sample_time_ms_ = millis(){
						return system_clock_ms;												// Source->FV	|	FV
					}
					Vo_read_->analogReadDebounced(...){
						Vo_raw_ = analogRead(myPins.Vom_pin);					// Source->FV	|	FV
					}
					Vo_ = float(Vo_raw_) * VO_CONV_GAIN;						// FV					| FV
				}
				sample_Vc(){
					Vc_read_->analogReadDebounced(...){
						Vc_raw_ = analogRead(myPins.Vc_pin);					// Source->FV	| FV
					}
					Vc_ = float(Vc_raw_) * VH3V3_CONV_GAIN;					// FV					| FV
				}
				sample_combine(){
					Vo_Vc_ = Vo_ - Vc_;															// FV					| FV
				}
			} // Sen->ShuntAmp->sample(...)

			Sen->ShuntNoAmp->sample(...){
				// ...similar to  ShuntAmp
			}

			Sen->ShuntAmp->convert(...){
				vshunt_ = Vo_Vc_;																	// FV				| FV
				Ishunt_cal_ = vshunt_ * SHUNT_AMP_GAIN ;					// FV				| FV
			}
			Sen->ShuntNoAmp->convert(...){
				// ...similar to  ShuntAmp
			}
			Sen->Flt->vc_check(...);  // OS fault check
			Sen->shunt_select_initial(...){
				Ib_amp_model_ = mod_add;													// FV				| FV
				Ib_noa_model_ = mod_add;													// FV				| FV

				Ib_amp_hdwe_ = ShuntAmp->Ishunt_cal(){						// FV				| FV
						return Ishunt_cal_ ;
				}
				Ib_noa_hdwe_ = ShuntNoAmp->Ishunt_cal(){
					// ... similar to ShuntAmp
				}
				Vc_hdwe_ = max(ShuntAmp->Vc(), ShuntNoAmp->Vc());// FV				| FV
				Vc_hdwe_sum_ = ShuntAmp->Vc() + ShuntNoAmp->Vc();// FV				| FV
			}

			// Assign Ib
			if (!sp.mod_ib()) {
				Ib_model_in_ = Ib_hdwe_;  												// n/a	| Feedback->PV
			} 
			else {
				Ib_noise = psuedo_random_binary_noise(bits=7, seed=...);		// n/a
				Ib_model_in_ = mod_add + Ib_noise;								// FV				| n/a
			}

			// vb load-----------------------------------
			Sen->vb_load(myPins.Vb_pin=D12, ...){
				Vb_raw_ = Vb_read_...;														// n/a	| Source->FV
				...
				Vb_hdwe_ = Vb_raw_ * VB_CONV_GAIN;								// FV		| FV
				// Note: T_ in following is UBC (past value) from previous frame
				Vb_hdwe_f_ = VbHdweFilt->calculate(..., AMP_FILT_TAU, T_, ...);	
																														// FV		| FV
				...
			}
			Sen->Flt->vb_check(...);														// FV		| FV

			// Tb load-----------------------------------
			Sen->Tb_load(myPins.VTb_pin=D0, ...){
				Tb_raw_ = Tb_read_ ...;														// n/a	| Source->FV
				...
				Tb_hdwe_ = thermistor_equation(Tb_raw_);					// n/a			| FV
				Tb_hdwe_f_ = TbHdweFilt->calculate(..., TB_FILT, T_, ...);
																													// n/a			| FV
				...
				Tb_model_ = NOMINAL_TB + Tb_noise();							// FV				| n/a
				Tb_model_f_ = TbModelFilt->calculate(..., TB_FILT, T_, ...);
																														// FV				| n/a
				...
			}
			Sen->Flt->Tb_check(...);  //--> TB_FLT, TB_FA				// FV				| FV
		}  // load_ib_vb_tb


		// Sim initialize as needed from memory
  		if (reset_temp) {
			initialize_all(Mon, Sen, 0., false);
		}
		Sen->Sim->apply_delta_q_t(reset);
		Sen->Sim->init_battery_sim(reset, Sen);
		Mon->init_battery_mon(reset, Sen);

		// Sim calculation
		Sen->Vb_model(Sen->Sim->calculate()){					// PV for Vb_model_	| same
			// Inputs
 			Tb_ = Sen->Tb(){
				return Tb_;																				// FV				| FV
			}
			// Inputs
 			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// FV				| FV
			}
			ib_in_ = Sen->Ib_model_in() / ap.nP();							// FV				| FV
			dt_ = dt_pst_;																			// FV				| FV
			ib_ = ib_pst_;																	// Feedback->PV | PV
			Sen->Ib_model(ib_pst_ * ap.nP(s)){
				Ib_model_ = input;																// PV				| PV
 			}
 			 // VOC-OCV model
			voc_stat_ = calc_soc_voc(soc_pst_, Tb_f_, ...){
				lookup(soc_pst_, Tb_f_, Y_T, X_SOC, T_VOC);
						// soc_pst_ = Feedback --> PV source; Tb_f = FV; voc_stat_ mixed (noted)
			}																										// PV				| PV
			voc_ = voc_stat_;																		// PV				| PV

			// ChargeTransfer dynamic model for model
			ib_dyn_ = ChargeTransfer_->calculate(ib_, reset, chem_.tau_ct, dt_);
																													// PV				| PV
			dvdyn_ =  ib_dyn_*chem_.r_ct  + ib_*chem_.r_0;	// PV				| PV
			vb_ = voc_ + dvdyn_;																// PV				| PV
			voc_soc_ = voc_stat_;																// PV				| PV

  			// Saturation logic, both full and empty
			// Pass along current to charge unless bms_off
			float ib_charge_pst = ib_in_;												// FV				| FV
			if ( sp.mod_ib )
				sat_ib_max_ = sat_ib_null_ + (1. - soc_pst_)*sat_cutback_gain_ ;
																													// PV
			else
				 // Disable cutback when real world
				sat_ib_max_ = ib_charge_pst;											// FV				| FV
			ib_pst_ = min(ib_charge_pst, sat_ib_max_);					// FV				| FV
			dt_charge_ = dt_pst_;																// FV				| FV
			ib_charge_ = ib_pst_;																// FV				| FV
			return vb_;																					// PV 			| PV
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
		Sen->select_volt_and_current_and_temp(){

			// ib select
			ib_choose_hi_lo() {   // Use the first argument and the table second
							   // argument to choose between 3rd and 4th arguments
				Ib_hdwe_ = scale_select( 		Ib_noa_hdwe_,   	sel_brk_hdwe,
											Ib_amp_hdwe_, 	Ib_noa_hdwe, ...)
																													// FV				| FV
				Ib_hdwe_model_ = scale_select(	Ib_noa_model_, 	sel_brk_hdwe,
											Ib_amp_model_, 	Ib_noa_model_, ...);
																													// FV				| FV
				sample_time_ib_hdwe_ = ShuntNoAmp->sample_time(){
							return sample_time_ms_;											// FV				| FV
				}
				dt_ib_hdwe_ms_ = ShuntNoAmp->dt_ms(){
					return return sample_time_ms_ - sample_time_z_ms_;
																													// FV				| FV
				}
			}

			// Tb select
			if (sp.mod_tb()) {  // Model Tb
				if (Flt->Tb_fa() ...) {
					....
	    			} else if (Flt->Tb_flt() ...) { // last good value while flt resolved
					...
					return;
				} else {
					Tb_ = Tb_model_;																// FV				| FV
					Tb_f_ = Tb_model_f_;														// FV				| FV
				}
			} else {  // Hardware Tb
				if (Flt->Tb_fa() ...) {
					...
				} else if (Flt->Tb_flt() ...) {  // last good value while flt resolved
					...
					return;
				} else {
					Tb_ = Tb_hdwe_;																	// FV				| FV
					Tb_f_ = Tb_hdwe_f_;															// FV				| FV
				}
			}

			// vb select
			if (sp.mod_vb()) {  // Model vb
				Vb_f_ = Vb_;																			// PV				| n/a
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...) {
					...
				} else {
					Vb_ = Vb_model_ + Vb_noise();										// FV				| n/a
				}
			} else {
				Vb_f_ = Vb_hdwe_f_;																// n/a			| FV
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...)) {
					...
				} else {
					Vb_ = Vb_hdwe_;																	// n/a			| FV
				}
  		}

			// ib
			if (sp.mod_ib()) {
				Ib_ = Ib_hdwe_model_;															// FV				| n/a
				Ib_amp_ = Ib_amp_model_;													// FV				| n/a
				Ib_noa_ = Ib_noa_model_;													// FV				| n/a
				Vc_ = HALF_V3V3;
				sample_time_ib_ = Sim->sample_time(){
					return sample_time_ms_;													// FV				| n/a
				}
				dt_ib_ms_ = Sim->dt_pst_ms(){
					return dt_pst_ms_;										// Feedback->PV				| n/a
				}
			} else {
				Ib_ = Ib_hdwe_;																		// n/a			| FV
				Ib_amp_ = Ib_amp_hdwe_;														// n/a			| FV
				Ib_noa_ = Ib_noa_hdwe_;														// n/a			| FV
				Vc_ = Vc_hdwe_;																		// n/a			| FV
				sample_time_ib_ = sample_time_ib_hdwe_;						// n/a			| FV
				dt_ib_ms_ = dt_ib_hdwe_ms_;												// n/a			| FV
			}
			T_ = double(dt_ib_ms_) / 1000.;  										// PV				| FV****
			now_ms_ = sample_time_ib_;													// FV				| FV
			c_time_ = double(now_ms_) / 1000.;									// FV				| FV
			Sim->assign_times(input=c_time_){
				dt_pst_ = input - c_time_;												// FV				| FV
				dt_pst_ms_ = (uint32_t)round(dt_pst_ * 1000.0);		// FV				| FV
				c_time_ = input;												// FV->Feedback		| FV->Feedback
			}
		} // select_volt_and_current_and_temp

		// Charge calculation and memory store
		Sen->Sim->count_coulombs() {
			// Inputs
			Tb_ = Sen->Tb(){
				return Tb_;																				// FV				| FV
			}
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// FV				| FV
			}

			// Saturation and re-init.   Goal is to set q_capacity and hold it so remember
			// last saturation status
			static bool reset_temp_past = reset_temp; 
							// needed because model called first in reset_temp path; need
											                 // to pick up latest
			if (initializing_all) reset_temp_past = true;
			if (!sp.mod_vb())  {  // Real world init sim to track Monitor SOC
				if (Mon->sat() || reset_temp_past) apply_delta_q(Mon->delta_q());
			} else {
				...
			}

			// Integration.   can go to -20%
			q_capacity_ = calculate_capacity(Tb_f_);						// FV				| FV
			// Coulomb Counting uses Backard Euler Integration
			d_delta_q_s_ = ib_charge_ * dt_charge_;							// PV				| PV
			if (ib_charge_ > 0.) d_delta_q_s_ *= coul_eff_;			// PV				| PV
			if (reset_temp) {
				*sp_delta_q_ = 0.;
			}
			if (!reset_temp_past) {
				*sp_delta_q_ += d_delta_q_s_;											// PV				| PV
				...
			}
			q_ = q_capacity_ + *sp_delta_q_;										// PV				| PV
			// Normalize
			soc_ = q_ / q_capacity_;														// PV				| PV

			// Save and return
			reset_temp_past = reset_temp;
			return soc_;																				// PV				| PV
		}  // Sen->Sim->count_coulombs

		Sen->Sim->calc_inj(...){
			  sample_time_s_ms_ = millis();											// Source->FV	| n/a
				inj_bias = ...;
			  sp.put_Inj_bias(inj_bias){
					inj_bias_ = input;	
				}
		}

	}  // sense_synth_select

	// Calculate Ah remaining
	monitor(...) {
		Mon->calculate(Sen, reset_temp, reset_ekf){
			// Inputs
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// FV				| FV
			}
			vsat_ = calc_vsat(){
  				return nom_vsat_ + (Tb_f_ - chem_.rated_temp) * chem_.dvoc_dt;
																													// FV				| FV
			}
			dt_ = Sen->T(){
				return T_;																				// PV				| FV*****
			}
			c_time_ = Sen->c_time_pst(){
				return c_time_;																		// FV				| FV
			}
			vb_ = Sen->vb(){
				return Vb_ / ap.nS();															// PV				| FV*****
			}
			ib_ = Sen->ib(){
				return Ib_ / sp.nP();															// FV				| FV
			}

			// Table lookup
			voc_soc_ = voc_soc_tab(soc_pst_, Tb_f_);								// PV				| PV
					// soc_pst_ is Feedback->PV; Tb_f is FV; voc_stat_ mixed (noted; neglect)

			// Battery management system model
			... /// --> bms_off, bms_charging, voltage_low

			// Charging
			ib_charge_ = ib_;																		// FV				| FV
			float ib_charge_ekf = ib_charge_;										// FV				| FV
			if (bms_off_ && !bms_charging_ && sp.mod_vb()) ib_charge_ = 0.;
			if (bms_off_ && voltage_low_) ib_ = 0.;

			if (reset_temp) ib_past_ = ib_;

			// Dynamic emf. vb_ is stale when running with model
			float ib_dyn_in;
			if (sp.mod_vb())  ib_dyn_in = ib_past_;				// Feedback->PV		| same
			else  ib_dyn_in = ib_;															// FV				| FV
			ib_dyn_ = ChargeTransfer_->calculate(ib_dyn_in, reset_temp, chem_.tau_ct,
																						dt_);
																													// PV				| FV*****
			float dvdyn = ib_dyn_ * chem_.r_ct + ib_dyn_in * chem_.r_0;
																													// PV				| FV*****
			voc_ = vb_ - dvdyn;																	// PV				| FV*****
			if ((bms_off_ && voltage_low_) || Sen->Flt->vb_fa_lt()) {
				...
			}
			dv_dyn_ = vb_ - voc_;																// PV				| FV*****

			// Hysteresis model
			... // not used

			// voc(soc) table
			voc_stat_ = calc_soc_voc(soc_pst_, Tb_f_, ...);					// PV				| PV
						// soc_pst_ = Feedback->PV; Tb_f = FV; voc_stat_ mixed (noted)
			voc_ = voc_stat_;																		// PV				| PV

			// Reversionary model
			vb_model_rev_ = voc_soc_ + dv_dyn_;									// PV				| mixed

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
				voc_stat_f_ = VocStatFilt->calculate(voc_stat_, reset_ekf ||
					reset_temp, ap.voc_stat_filt(), dt_ekf_);
				if (reset_ekf) {
					solve_ekf(reset_ekf, reset_temp, Sen);
				}  else {
					predict_ekf(ddq_dt, freeze_ekf_);         // u = d(dq)/dt
					update_ekf(voc_stat_f_, 0., MXEPS); 
						// hx, predicted = est past
				}
				soc_ekf_ = x();  // x = Vsoc (0-1 ideal capacitor voltage) proxy for soc
				q_ekf_ = soc_ekf_ * q_capacity_;
				delta_q_ekf_ = q_ekf_ - q_capacity_;
				y_ekf_ = y();  // y = z - hx, residual between measurement and predicted
				// measurement
				y_ekf_f_ = Yfilt->calculate(y_ekf_, reset_temp, dt_ekf_);

				// EKF convergence
				bool conv = abs(y_ekf_f_) < ap.ekf_conv() &&
					 !cp.soft_reset && !cp.ekf_reset;  // Initialize false
				ekf_conv_ = EKF_converged->calculate(conv, EKF_T_CONV, EKF_T_RES, ...)

				if (reset_ekf) cp.ekf_reset = false;
			}
			eframe_++;
			if (reset_temp || reset_ekf || cp.soft_reset || eframe_>=ap.eframe_mult())
			eframe_ = 0;  // '>=' allows changing ap.eframe_mult() on the fly

			// Deadband filter
			voc_dead_ = SdVb_->update(voc_);  // used for saturation test
																													// PV				| PV

			// Charge time if used ekf
			tcharge_ekf = time_to_completion(soc_ekf_, ib_charge_)

			// Past value for synchronization with vb_, only when modeling
			ib_past_ = ib_;															// FV for feedback	| same

			return vb_model_rev_;																// PV				| mixed
		}  // Mon->calculate

		// Debounce saturation calculation done in ekf using voc model
		Sen->sat(Mon->is_sat(reset));
		Sen->saturated(Is_sat_delay->calculate(Sen->sat(), T_SAT, T_DESAT, ...));

		// Memory store (Count Coulombs)
		float cc_ib_in = Mon->ib_charge();
		if (Sen->Flt->ib_amp_fa() && Sen->Flt->ib_noa_fa() && !ap.fake_faults())
		cc_ib_in = 0.;
		Mon->count_coulombs(Sen, reset_temp, charge_current=Mon.ib_charge(),
																		Sen->sat(), Sen->saturated()) {
			// Inputs
			dt_ = Sen->T(){
				return T_;																				// PV				| FV****
			}
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// FV				| FV
			}
			charge_curr = Mon.ib_charge(){
				return ib_;																				// FV				| FV
			}
			d_delta_q_ = charge_curr * dt_;											// mixed		| FV****

			// State change
			double d_delta_q_inf = d_delta_q_;									// mixed		| FV****
			...

			// Integration.   Can go to negative
			q_capacity_ = calculate_capacity(Tb_f_);						// FV				| FV
			if (!reset_temp) *sp_delta_q_ += d_delta_q_;				// mixed		| FV****
			q_ = q_capacity_ + *sp_delta_q_;										// mixed		| FV****

			// Normalize
			soc_ = q_ / q_capacity_;														// mixed		| FV****

			return soc_;																				// mixed		| FV****
		}  // Mon->count_coulombs

		// Charge charge time for display
		Mon->calc_charge_time(
									Mon->q(){ return q_;},							// mixed		| FV****	|
									Mon->q_capacity(){return q_capacity_},// mixed 	| FV****	|
									Sen->ib(){ return ib_ },						// FV 			| FV			|
									Mon->soc(){ return soc_});					// mixed		| FV****	v
																													=	// mixed		| FV****
	}  // monitor

	// Print
	print_...

	// Manage states
	Sen->Sim->data_of_future_passed(...) {
	  sample_time_s_pst_ms_ = sample_time_s_ms_;						// Feedback->FV	| n/a
    soc_pst_ = soc_;
	}
	Mon->data_of_future_past(...) {
 		...
    soc_pst_ = soc_;
	}

}  // read
}  // loop
```
