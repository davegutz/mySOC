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

/* Key:
ZV = past value
PV = present value
Values for loc in far right columns						// Model temporal | Hdwe temporal
*/


// Loop
loop() {
read = wait_for_update(READ_DELAY);
if (read) {

	// Manage states
	Sen->Sim->data_of_future_past(reset){
		sample_time_s_pst_ms_ = sample_time_s_ms_;				// Feedback->ZV | ZV
	  soc_pst_ = soc_;																	// Feedback->ZV | ZV
	}
	Mon->data_of_future_passed(reset){
	  soc_pst_ = soc_;																	// Feedback->ZV | ZV
	}

	// Read sensors, model signals, select between them, synthesize injection
  sense_synth_select(...) {
		load_ib_vb_tb(){
			// ib load-----------------------------------
			// Sample Ib
			Sen->ShuntAmp->sample(...) {
				sample_Vo(){			
					sample_time_z_ms_ = sample_time_ms_;				// Feedback->ZV | ZV
					sample_time_ms_ = millis(){
						return system_clock_ms;											// Source->PV	|	PV
					}
					Vo_read_->analogReadDebounced(...){
						Vo_raw_ = analogRead(myPins.Vom_pin);				// Source->PV	|	PV
					}
					Vo_ = float(Vo_raw_) * VO_CONV_GAIN;						// PV				| PV
				}
				sample_Vc(){
					Vc_read_->analogReadDebounced(...){
						Vc_raw_ = analogRead(myPins.Vc_pin);				// Source->PV	| PV
					}
					Vc_ = float(Vc_raw_) * VH3V3_CONV_GAIN;					// PV				| PV
				}
				sample_combine(){
					Vo_Vc_ = Vo_ - Vc_;															// PV				| PV
				}
			} // Sen->ShuntAmp->sample(...)

			Sen->ShuntNoAmp->sample(...){
				// ...similar to  ShuntAmp
			}

			Sen->ShuntAmp->convert(...){
				vshunt_ = Vo_Vc_;																	// PV				| PV
				Ishunt_cal_ = vshunt_ * SHUNT_AMP_GAIN ;					// PV				| PV
			}
			Sen->ShuntNoAmp->convert(...){
				// ...similar to  ShuntAmp
			}

			Sen->Flt->vc_check(...);  // OS fault check

			Sen->shunt_select_initial(...){
				if (!sp.mod_ib()) {
					mod_add = 0.;
					hdwe_add = ... + sp.inj_bias(){ return inj_bias_ };
																													// n/a			| ZV   ok
				} else {
					mod_add = ... + sp.inj_bias(){ return inj_bias_ };
																													// ZV				| n/a   ok
					hdwe_add = 0.;
					...
				}
									// ok because exact time that mod_add is generated isn't 
									// tracked by any logic.  xxx_model_ is considered source
									// mod_add is ZV of an independent source. ok->consider it PV
				Ib_amp_model_ = mod_add;	// ok->consider it PV		// PV				| PV
				Ib_noa_model_ = mod_add;	// ok->consider it PV		// PV				| PV

				Ib_amp_hdwe_ = ShuntAmp->Ishunt_cal(){
						return Ishunt_cal_ ;													// PV				| PV
				}
				Ib_noa_hdwe_ = ShuntNoAmp->Ishunt_cal(){
					// ... similar to ShuntAmp
				}
				Vc_hdwe_ = max(ShuntAmp->Vc(), ShuntNoAmp->Vc());	// PV				| PV
				...
			}

			Sen->ib_choose_hi_lo(){
				Ib_hdwe_ = f(Ib_amp_hdwe_, Ib_noa_hdwe_);					// n/a			| PV
			}

			// Assign Ib for model
			if (!sp.mod_ib()) {
				Ib_model_in_ = Ib_hdwe_;  												// n/a	| Feedback->ZV
			} 
			else {
				Ib_noise = psuedo_random_binary_noise(...);				// n/a 			| n/a
				Ib_model_in_ = mod_add + Ib_noise;								// PV				| n/a
			}

			// vb load-----------------------------------
			Sen->vb_load(myPins.Vb_pin=D12, ...){
				Vb_raw_ = Vb_read_...;														// n/a	| Source->PV
				...
				Vb_hdwe_ = Vb_raw_ * VB_CONV_GAIN;								// PV				| PV
				...
			}
			Sen->Flt->vb_check(...);														// PV				| PV

			// Tb load-----------------------------------
			Sen->Tb_load(myPins.VTb_pin=D0, ...){
				Tb_raw_ = Tb_read_ ...;														// n/a	| Source->PV
				...
				Tb_hdwe_ = thermistor_equation(Tb_raw_);					// n/a			| PV
				Tb_hdwe_f_ = TbHdweFilt->calculate(..., TB_FILT, T_, ...);
																													// n/a			| mixed***
				...
				Tb_model_ = NOMINAL_TB + Tb_noise();							// PV				| n/a
				Tb_model_f_ = TbModelFilt->calculate(..., TB_FILT, T_, ...);
																													// mixed| mixed *****
				...
			}
			Sen->Flt->Tb_check(...);  //--> TB_FLT, TB_FA				// PV				| PV
		}  // load_ib_vb_tb


		// Sim initialize as needed from memory
		...

		// Sim calculation
		Sen->Sim->calculate()){	
			// Inputs
 			Sim::Tb_ = Sen->Tb(){
				return Tb_;																				// ZV				| ZV
			}
			// Inputs
 			Sim::Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// ZV				| ZV
			}
			Sim::ib_in_ = (Sen->Ib_model_in(){return Sen::Ib_model_in_} / ap.nP());
																													// PV				| PV
			Sim::dt_ = Sim::dt_pst_s_;													// ZV   		| ZV
			Sim::ib_ = Sim::ib_pst_;												// Feedback->ZV | ZV
			Sen->Ib_model(Sim::ib_pst_ * ap.nP(s)){
				Sen::Ib_model_ = input;														// ZV				| ZV
 			}
 			 // VOC-OCV model
			Sim::voc_stat_ = calc_soc_voc(soc_pst_, Tb_f_, ...){
				lookup(soc_pst_, Tb_f_, ...);
			}																										// ZV				| ZV
			Sim::voc_ = voc_stat_;															// ZV				| ZV

			// ChargeTransfer dynamic model for model
			Sim::ib_dyn_ = ChargeTransfer_->calculate(ib_, ..., dt_);
																													// ZV				| ZV
			Sim::dvdyn_ =  Sim::ib_dyn_*chem_.r_ct  + Sim::ib_*chem_.r_0;
																													// ZV				| ZV
			Sim::vb_ = Sim::voc_ + Sim::dvdyn_;									// ZV				| ZV
			Sim::voc_soc_ = Sim::voc_stat_;											// ZV				| ZV

  		// Saturation logic, both full and empty.  Special Sim logic
			float ib_charge_pst = Sim::ib_in_;									// PV				| PV
			if ( sp.mod_ib )
				Sim::sat_ib_max_ = Sim::sat_ib_null_ +
											(1. - Sim::soc_pst_)*Sim::sat_cutback_gain_ ;
																													// ZV				| n/a
			else
				// Disable cutback when real world
				Sim::sat_ib_max_ = ib_charge_pst;									// PV				| PV
			Sim::ib_pst_ = min(ib_charge_pst, Sim::sat_ib_max_);
																													// PV				| PV
			Sim::dt_charge_s_ = Sim::dt_pst_s_;									// PV				| PV
			Sim::ib_charge_ = Sim::ib_pst_;											// PV				| PV
			return vb_;																					// ZV 			| ZV
		} // Sen->Sim->calculate()

		Sen->Vb_model(Sen->Sim->calculate()){
			Vb_model_ = Sen->Sim->vb_;									// ZV for Vb_model_	| same
		}

		// Fault Logic, & Selection Logic - selection status and fault reset
		...

		// Apply Fault Logic to select signals
		Sen->select_volt_and_current_and_temp(){

			// ib select
			ib_choose_hi_lo() {   // Use the first argument and the table second
							   // argument to choose between 3rd and 4th arguments
				Ib_hdwe_ = scale_select( 		Ib_noa_hdwe_,   	sel_brk_hdwe,
											Ib_amp_hdwe_, 	Ib_noa_hdwe, ...)
																													// PV				| PV
				Ib_hdwe_model_ = scale_select(	Ib_noa_model_, 	sel_brk_hdwe,
											Ib_amp_model_, 	Ib_noa_model_, ...);
																													// PV				| PV
			}
			dt_ib_hdwe_ms_ = ShuntNoAmp->dt_ms(){
				return sample_time_ms_ - sample_time_z_ms_;
																													// PV				| PV
			}

			// Tb select
			if (sp.mod_tb()) {  // Model Tb
				if (Flt->Tb_fa() ...) {
					....
				} else if (Flt->Tb_flt() ...) {
					...
					return;
				} else {
					Tb_ = Tb_model_;																// PV				| PV
					Tb_f_ = Tb_model_f_;														// mixed		| mixed
				}
			} else {  // Hardware Tb
				if (Flt->Tb_fa() ...) {
					...
				} else if (Flt->Tb_flt() ...) {
					...
					return;
				} else {
					Tb_ = Tb_hdwe_;																	// PV				| PV
					Tb_f_ = Tb_hdwe_f_;															// PV				| PV
				}
			}

			// vb select
			if (sp.mod_vb()) {  // Model vb
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...) {
					...
				} else {
					Vb_ = Vb_model_ + Vb_noise();										// ZV				| n/a
				}
			} else {
				if ((Flt->wrap_vb_fa() || Flt->vb_fa_lt()) ...)) {
					...
				} else {
					Vb_ = Vb_hdwe_;																	// n/a			| PV
				}
  		}

			// ib select
			update_dt() {
			  if (sp.mod_ib()) {
  			  sample_time_ib_ms_ = Sim->sample_time_s(){
						return sample_time_s_ms_;							//
					};
					dt_ib_ms_ = Sim->dt_pst_s_ms(){
						return dt_pst_s_ms_;								// Feedback->ZV				| n/a
					}
  			} else {
    			sample_time_ib_ms_ = sample_time_ib_hdwe_ms_;
    			dt_ib_ms_ = dt_ib_hdwe_ms_;											// PV				| PV
			  }
  			T_ = double(dt_ib_ms_) / 1000.;
			}
			if (sp.mod_ib()) {
				Ib_ = Ib_hdwe_model_;															// PV				| n/a
				Ib_amp_ = Ib_amp_model_;													// PV				| n/a
				Ib_noa_ = Ib_noa_model_;													// PV				| n/a
				Vc_ = HALF_V3V3;
			} else {
				Ib_ = Ib_hdwe_;																		// n/a			| PV
				Ib_amp_ = Ib_amp_hdwe_;														// n/a			| PV
				Ib_noa_ = Ib_noa_hdwe_;														// n/a			| PV
				Vc_ = Vc_hdwe_;																		// n/a			| PV
			}
			now_ms_ = sample_time_ib_ms_ + ...;									// PV				| PV
			c_time_s_ = double(now_ms_) / 1000.;								// PV				| PV
			Sim->assign_times(input=c_time_s){
				dt_pst_s_ = input - c_time_s_;										// PV				| PV
				dt_pst_s_ms_ = (uint32_t)round(dt_pst_s_ * 1000.0);
																								// PV->Feedback		| PV->Feedback
				c_time_s_ = input;											// PV->Feedback		| PV->Feedback
			}
		} // select_volt_and_current_and_temp

		// Charge calculation and memory store
		Sen->Sim->count_coulombs() {
			// Inputs
			Tb_ = Sen->Tb(){
				return Tb_;																				// PV				| PV
			}
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// PV				| PV
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
			q_capacity_ = calculate_capacity(Tb_f_);						// mixed		| mixed
			// Coulomb Counting uses Backard Euler Integration
			d_delta_q_s_ = ib_charge_ * dt_charge_s_;						// ZV				| ZV
			if (ib_charge_ > 0.) d_delta_q_s_ *= coul_eff_;			// ZV				| ZV
			if (reset_temp) {
				*sp_delta_q_ = 0.;
			}
			if (!reset_temp_past) {
				*sp_delta_q_ += d_delta_q_s_;											// ZV				| ZV
				...
			}
			q_ = q_capacity_ + *sp_delta_q_;										// mixed		| mixed
			// Normalize
			soc_ = q_ / q_capacity_;														// mixed		| mixed

			// Save and return
			reset_temp_past = reset_temp;
			return soc_;																				// ZV				| ZV
		}  // Sen->Sim->count_coulombs


		// Injection test executive
		if ((Sen->start_inj(){ return start_inj_ms_(pst); } <= Sen->now_ms(){return now_ms_;}) &&
				(Sen->now_ms(){return now_ms_;} <= Sen->end_inj(){ return end_inj_ms_; }) &&
				(Sen->now_ms(){return now_ms_;} > 0ULL))  // in range, test in progress
		{
			// Shift times because sampling is asynchronous: improve repeatibility
			...


			// Put a stop to this but retain sp.amp_ to scale fault and history
			// printouts properly
			...

		} // injection test executive

		// Injection bias
		Sen->Sim->calc_inj(...){
			  sample_time_s_ms_ = millis();											// Source->PV	| n/a
				inj_bias = ...;																		// Source->PV	| n/a
			  sp.put_Inj_bias(inj_bias){
					inj_bias_ = input;															// PV					| n/a
				}
		}  // Injection bias

	}  // sense_synth_select

	// Calculate Ah remaining
	monitor(...) {
		Mon->calculate(Sen, reset_temp, reset_ekf){
			// Inputs
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// PV				| PV
			}
			vsat_ = calc_vsat(){
  				return nom_vsat_ + (Tb_f_ - chem_.rated_temp) * chem_.dvoc_dt;
																													// PV				| PV
			}
			dt_ = Sen->T(){
				return T_;																				// ZV				| PV*****
			}
			c_time_ = Sen->c_time_pst(){
				return c_time_;																		// PV				| PV
			}
			vb_ = Sen->vb(){
				return Vb_ / ap.nS();															// ZV				| PV*****
			}
			ib_ = Sen->ib(){
				return Ib_ / sp.nP();															// PV				| PV
			}

			// Table lookup
			voc_soc_ = voc_soc_tab(soc_pst_, Tb_f_);						// ZV				| ZV
					// soc_pst_ is Feedback->ZV; Tb_f is PV; voc_stat_ mixed (noted; neglect)

			// Battery management system model
			... /// --> bms_off, bms_charging, voltage_low

			// Charging
			ib_charge_ = ib_;																		// PV				| PV
			float ib_charge_ekf = ib_charge_;										// PV				| PV
			if (bms_off_ && !bms_charging_ && sp.mod_vb()) ib_charge_ = 0.;
			if (bms_off_ && voltage_low_) ib_ = 0.;

			if (reset_temp) ib_past_ = ib_;

			// Dynamic emf. vb_ is stale when running with model
			float ib_dyn_in;
			if (sp.mod_vb())  ib_dyn_in = ib_past_;				// Feedback->ZV		| same
			else  ib_dyn_in = ib_;															// PV				| PV
			ib_dyn_ = ChargeTransfer_->calculate(ib_dyn_in, reset_temp, chem_.tau_ct,
																						dt_);
																													// ZV				| PV*****
			float dvdyn = ib_dyn_ * chem_.r_ct + ib_dyn_in * chem_.r_0;
																													// ZV				| PV*****
			voc_ = vb_ - dvdyn;																	// ZV				| PV*****
			if ((bms_off_ && voltage_low_) || Sen->Flt->vb_fa_lt()) {
				...
			}
			dv_dyn_ = vb_ - voc_;																// ZV				| PV*****

			// Hysteresis model
			... // not used

			// voc(soc) table
			voc_stat_ = calc_soc_voc(soc_pst_, Tb_f_, ...);			// ZV				| ZV
						// soc_pst_ = Feedback->ZV; Tb_f = PV; voc_stat_ mixed (noted)
			voc_ = voc_stat_;																		// ZV				| ZV

			// Reversionary model
			vb_model_rev_ = voc_soc_ + dv_dyn_;									// ZV				| mixed

			// EKF 1x1
			cp.ekf_executing = false;
			if (eframe_ == 0 || reset_ekf) {
				cp.ekf_executing = true;
				static uint64_t ekf_now_past = Sen->now_ms();
				float ddq_dt = ib_charge_ekf;

				// Freeze EKF with voltage fault or bms_off
				freeze_ekf_ = Sen->Flt->vb_fa_lt() || bms_off_;

				now_ekf_ = Sen->now_ms();
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
																													// ZV				| ZV

			// Charge time if used ekf
			tcharge_ekf = time_to_completion(soc_ekf_, ib_charge_)

			// Past value for synchronization with vb_, only when modeling
			ib_past_ = ib_;															// PV for feedback	| same

			return vb_model_rev_;																// ZV				| mixed
		}  // Mon->calculate

		// Debounce saturation calculation done in ekf using voc model
		...

		// Memory store (Count Coulombs)
		float cc_ib_in = Mon->ib_charge();
		if (Sen->Flt->ib_amp_fa() && Sen->Flt->ib_noa_fa() && !ap.fake_faults())
			cc_ib_in = 0.;
		Mon->count_coulombs(Sen, reset_temp, charge_current=Mon.ib_charge(),
																		Sen->sat(), Sen->saturated()) {
			// Inputs
			dt_ = Sen->T(){
				return T_;																				// ZV				| PV****
			}
			Tb_f_ = Sen->Tb_f(){
				return Tb_f_;																			// PV				| PV
			}
			charge_curr = Mon.ib_charge(){
				return ib_;																				// PV				| PV
			}
			d_delta_q_ = charge_curr * dt_;											// mixed		| PV****

			// State change
			double d_delta_q_inf = d_delta_q_;									// mixed		| PV****
			...

			// Integration.   Can go to negative
			q_capacity_ = calculate_capacity(Tb_f_);						// mixed		| mixed***
			if (!reset_temp) *sp_delta_q_ += d_delta_q_;				// mixed		| PV****
			q_ = q_capacity_ + *sp_delta_q_;										// mixed		| PV****

			// Normalize
			soc_ = q_ / q_capacity_;														// mixed		| PV****

			return soc_;																				// mixed		| PV****
		}  // Mon->count_coulombs

		// Charge charge time for display
		Mon->calc_charge_time(
									Mon->q(){ return q_;},							// mixed		| PV****	|
									Mon->q_capacity(){return q_capacity_},// mixed 	| PV****	|
									Sen->ib(){ return ib_ },						// PV 			| PV			|
									Mon->soc(){ return soc_});					// mixed		| PV****	v
																													=	// mixed		| PV****
	}  // monitor

	// Print
	print_...

	// Talk
	Sen->start_inj(Sen->now{}{return now_ms_;}) {
		start_inj_ms_(pst) = now_ms_;
	}

	// Manage states
	Sen->Sim->data_of_future_passed(...) {
	  sample_time_s_pst_ms_ = sample_time_s_ms_;				// PV->Feedback		| n/a
    soc_pst_ = soc_;
	}
	Mon->data_of_future_past(...) {
 		...
    soc_pst_ = soc_;
	}

}  // read
}  // loop
```
