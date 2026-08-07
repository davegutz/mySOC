Top Level Minor Frame
```c++
if (read) {

	// Sample Ib
	Sen->ShuntAmp->sample(...) {
		sample_Vo(){
			sample_time_z_ = sample_time_;
			sample_time_ = millis();
 		 	Vo_raw_ = Vo_read_->analogReadDebounced(...);
  			Vo_ = float(Vo_raw_) * VO_CONV_GAIN;
  		}
  		sample_Vc(){
  			Vc_raw_ = Vc_read_->analogReadDebounced(...);
    			Vc_ = float(Vc_raw_) * VH3V3_CONV_GAIN;
  		}
  		sample_combine(){
			Vo_Vc_ = Vo_ - Vc_;
  		}
	}

 	Sen->ShuntNoAmp->sample(...){
		...same as ShuntAmp
	}

 	// Read sensors, model signals, select between them, synthesize injection
  	sense_synth_select(...) {

		load_ib_vb_tb(){

			// ib load
			Sen->ShuntAmp->convert(...){
				vshunt_ = Vo_Vc_;
				Ishunt_cal_ = vshunt_ * v2a_s_ ;
			}
			Sen->ShuntNoAmp->convert(...){
				...same as ShuntAmp
			}
			Sen->Flt->vc_check(...);
			Sen->shunt_select_initial(...){

  				Ib_amp_model_ = mod_add;
				Ib_noa_model_ = mod_add;

				Ib_amp_hdwe_ = ShuntAmp->Ishunt_cal();
  				Ib_noa_hdwe_ = ShuntNoAmp->Ishunt_cal();

				Vc_hdwe_ = max(ShuntAmp->Vc(), ShuntNoAmp->Vc());
				Vc_hdwe_sum_ = ShuntAmp->Vc() + ShuntNoAmp->Vc();
			}
			ib_choose_hi_lo();  // Initial choice
			// When running normally the model tracks hdwe to synthesize reference
			if (!sp.mod_ib()) {
				Ib_model_in_ = Ib_hdwe_;
			} 
			// Otherwise it generates signals for feedback into monitor
			else {
				Ib_model_in_ = mod_add + Ib_noise();
			}

			// vb load
			Sen->vb_load(myPins->Vb_pin, ...){
			}
			Sen->Flt->vb_check(...);

			// Tb load
			Sen->Tb_load(myPins->VTb_pin, ...){
				Tb_raw_ = Tb_read_ ...;
				...
				Tb_hdwe_ = thermistor_equation(Tb_raw_);
				...
				Tb_model_ = NOMINAL_TB + Tb_noise();
				...
			}
			Sen->Flt->Tb_check(...);
		}

		// Sim calculation
		Sen->Vb_model(Sen->Sim->calculate());{
			// Inputs
  			Tb_ = Sen->Tb();
 			Tb_f_ = Sen->Tb_f();
			dt_in_ = (sample_time_ - sample_time_z_) / 1000.;
			ib_in_ = Sen->Ib_model_in() / ap.nP();
			dt_ = dt_fut_;
			ib_ = ib_fut_;
			Sen->Ib_model( ib_fut_ );
  
 			 // VOC-OCV model
			voc_stat_ = calc_soc_voc(soc_, Tb_f_, ...);


			// ChargeTransfer dynamic model for model
			ib_dyn_ = ChargeTransfer_->calculate(ib_, reset, chem_.tau_ct, dt_);
			dvdyn_ =  ib_dyn_ * chem_.r_ct  + ib_ * chem_.r_0;
			vb_ = voc_ + dvdyn;
			voc_soc_ = voc_stat_;

  			// Saturation logic, both full and empty
			if ( sp.mod_ib )
				sat_ib_max_ = sat_ib_null_ + (1. - (soc_ + ap.ds_voc_soc())) *  sat_cutback_gain_ ;
			else
				sat_ib_max_ = ib_charge_fut;  // Disable cutback when real world
			float ib_charge_fut = ib_in_;  // Pass along current to charge unless bms_off
			ib_fut_ = min(ib_charge_fut, sat_ib_max_);  // the feedback of ib_

			dt_charge_ = dt_fut_;
			ib_charge_ = ib_fut_;  // Same time plane as volt calcs, added past value

			return vb_;
		}

		// Fault logic
		Sen->Flt->ib_range();
		Sen->Flt->ib_logic();
		Sen->Flt->ib_wrap();
		Sen->Flt->ib_quiet();
		Sen->Flt->cc_diff();
		Sen->Flt->ib_diff();
		Sen->Flt->select_all_logic(){ // Select Logic - selection status and reset
			// Ib decision tables
			ib_decision_hi_lo(Sen){
   				ib_choice_ = ...;
				latch_ = ...;
				ib_decision_ = ...;
			}
		}


		// Apply Fault Logic to select signals
		Sen->select_volt_and_current_and_temp()){

			// ib select
			ib_choose_hi_lo(){
				// No failure
				Ib_hdwe_ = scale_select(Ib_noa_hdwe_,   sel_brk_hdwe,
										Ib_amp_hdwe_, Ib_noa_hdwe, ...)
				Ib_hdwe_f_ = scale_select(Ib_noa_hdwe_, sel_brk_hdwe,
										Ib_amp_hdwe_f_, Ib_noa_hdwe_f_, ...);
				Ib_hdwe_model_ = scale_select(Ib_noa_model_, sel_brk_hdwe,
										Ib_amp_model_, Ib_noa_model_, ...);
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
					Vb_ = Mon->vb_model_rev() * ap.nS();
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
				Ib_f_ = Ib_;
				Ib_amp_ = Ib_amp_model_;
				Ib_noa_ = Ib_noa_model_;
				Vc_ = HALF_V3V3;
				sample_time_ib_ = Sim->sample_time();
				dt_ib_ = Sim->dt_fut_ms();
			} else {
				Ib_ = Ib_hdwe_;
				Ib_f_ = Ib_hdwe_f_;
				Ib_amp_ = Ib_amp_hdwe_;
				Ib_noa_ = Ib_noa_hdwe_;
				Vc_ = Vc_hdwe_;
				sample_time_ib_ = sample_time_ib_hdwe_;
				dt_ib_ = dt_ib_hdwe_;
			}
			T_ = double(dt_ib_) / 1000.;  // s
			now_ = sample_time_ib_ - inst_millis_ + inst_time_ * 1000;
			Sim->assign_times(input=double(now_) / 1000.){
				dt_fut_ = input - c_time_;
				c_time_ = input;
			}
		}

		// Charge calculation and memory store
		Sen->Sim->count_coulombs();
	}

	// Calculate Ah remaining
	monitor(...);

	// Print
	print_...

}
```
