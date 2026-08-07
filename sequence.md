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
			Sen->ShuntAmp->convert(...){
				vshunt_ = Vo_Vc_;
				Ishunt_cal_ = vshunt_ * v2a_s_ ;
			}
			Sen->ShuntNoAmp->convert(...){
				...same as ShuntAmp
			}
			Sen->Flt->vc_check(...);
			Sen->shunt_select_initial(...){
  				Ib_amp_model_ = max(min(mod_add..., Ib_amp_max()), Ib_amp_min());  // uses past Ib
				Ib_noa_model_ = max(min(mod_add..., Ib_noa_max()), Ib_noa_min());  // uses past Ib
				Ib_amp_hdwe_ = ShuntAmp->Ishunt_cal();
				Vc_hdwe_ = max(ShuntAmp->Vc(), ShuntNoAmp->Vc());
				Vc_hdwe_sum_ = ShuntAmp->Vc() + ShuntNoAmp->Vc();
  				Ib_noa_hdwe_ = ShuntNoAmp->Ishunt_cal();

			// Initial choice
			ib_choose_hi_lo();

			// When running normally the model tracks hdwe to synthesize reference
			if (!sp.mod_ib()) {
				Ib_model_in_ = Ib_hdwe_;
			} 
			// Otherwise it generates signals for feedback into monitor
			else {
				Ib_model_in_ = mod_add;
			}

			Sen->vb_load(myPins->Vb_pin, ...);
			Sen->Flt->vb_check(...);
			Sen->Tb_load(myPins->VTb_pin, ...);
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

		// Select Logic
		Sen->Flt->select_all_logic());
		Sen->select_volt_and_current_and_temp());
  Sim->assign_times(c_time_);


		// Charge calculation and memory store
		Sen->Sim->count_coulombs();
	}

	// Calculate Ah remaining
	monitor(...);

	// Print
	print_...

}
```
