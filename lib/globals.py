
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
menu = None # Menu subsystem
switch_poller = None # Switch polling subsystem

# Global variables
cal_data = None
encoder_q = None # heapq for knob object
band_table = None
user_config_settings = None

tuning_increment_table = [100,500,1000,10000]


# Default settings
cal_file_path = "config/cal_values.json"
cal_defaults = {"si5351_correction_ppb":0, "xtal_freq_hz":25000000, "cf_frequency_hz":12288000, "cf_bandwith_hz":2000}

band_table_path = "config/band_table.json"
band_table_default = {"40M":{"low_limit":7000000, "high_limit":7300000}}

# User config settings
user_config_settings_path = "config/user_config.json"
user_config_settings_default = {"initial_freq": 7200000}


error_log_path = "log/errors.log"