# Clearing any previous versions of standard models before commensing.
find . -name "sm1_*.mod" -type f -delete
find . -name "sm2_*.mod" -type f -delete

# Depends on neuron (any many steps further installation)
python compile_nrn_mech.py icg-channels-K
python compile_nrn_mech.py icg-channels-Na
python compile_nrn_mech.py icg-channels-Ca
python compile_nrn_mech.py icg-channels-KCa
python compile_nrn_mech.py icg-channels-IH

# Uses HHanalyze.py in current dir (this is slighty modified from original version for convenience)
# Produces when possible, at 3 temps, SS and tau curves for all gates.
# Also dumps a log.txt file to inspect what happened during simulation
python extract_gates.py icg-channels-K
python extract_gates.py icg-channels-Na
python extract_gates.py icg-channels-Ca
python extract_gates.py icg-channels-IH
python extract_gates.py icg-channels-KCa  # This runs for 3 Ca concs. 5e-5, 5e-4, 5e-3

# CAUTION: Clears all previous versions of the *.pkl files
# This results in an updated icg-channels-*.pkl files (THIS IS PREPROCESSING ONLY)
# Uses sniff.py (has the abs path to the custom code)
python extract_gvals.py icg-channels-K
python extract_gvals.py icg-channels-Na
python extract_gvals.py icg-channels-Ca
python extract_gvals.py icg-channels-IH
python extract_gvals.py icg-channels-KCa

# CAUTION: This updates the *.pkl files with Q10 values and HHAnalyse flags
# This results in an updated icg-channels-*.pkl files (THIS IS PREPROCESSING ONLY)
python extract_temps.py icg-channels-K
python extract_temps.py icg-channels-Na
python extract_temps.py icg-channels-Ca
python extract_temps.py icg-channels-IH
python extract_temps.py icg-channels-KCa

## Caution: this updates the *.pkl files (K, Ca, Na and IH) with omni model fits
## DEFAULT is at 6.3 deg C [no SM's if not available at this temp]
python omnimodel_fits.py icg-channels-K
python omnimodel_fits.py icg-channels-Na
python omnimodel_fits.py icg-channels-Ca
python omnimodel_fits.py icg-channels-IH


# CAUTION: This updates the *.pkl files with .dat files and updates these values into
# the dictionary (THIS IS PREPROCESSING ONLY)
python update_dicts.py icg-channels-K
python update_dicts.py icg-channels-Na
python update_dicts.py icg-channels-Ca
python update_dicts.py icg-channels-IH
python update_dicts.py icg-channels-KCa

