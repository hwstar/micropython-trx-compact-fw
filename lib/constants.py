##################################
# Constants shared across modules#
##################################

PTT_DELAY_TIME = const(250) # Time delay between PTT and mute
KNOB_LONG_PRESS_TIME = const(1000) # Time for knob to be held down to register a long press
TX_TIME_OUT_TIME = const(600000) # 10 minute TOT
GC_COLLECT_INTERVAL = const(30000) # 30 seconds


# Transmit states used by display and vfo
TXS_RX = 0
TXS_TX = 1
TXS_TUNE = 2
TXS_TIMEOUT = 3

# Emission modes
TXM_LSB = 0
TXM_USB = 1