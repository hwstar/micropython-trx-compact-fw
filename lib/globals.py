#
# This file contains objects which need to be accessed by multiple modules
#

# Global objects

lcd = None # LCD object
knob = None # Encoder knob object
cal = None # Calibration data object
i2c = None # I2C communication object
si5351 = None # Programable clock oscillator
event = None # Event subsystem
vfo = None # VFO subsystem

# Global variables
cal_data = None
encoder_q = None # heapq for knob object


# Default settings
cal_file_dir = "config/cal_values.json"
cal_defaults = {"si5351_correction_ppb":0, "xtal_freq_hz":25000000, "cf_frequency_hz":12288000, "cf_bandwith_hz":2000}