from machine import I2C,Pin,Timer
import micropython
import gc
import time
from lib.configrw import ConfigRw
import event as ev
import uheapq as q
import lib.globals as g
import lib.gpiopins as pins
import lib.gpio_lcd as lcd
import lib.encoder_knob as knob
import lib.si5351 as clkgen
import lib.vfo as vfo


########################################
# Classes for use by this module only  #
########################################

#
# This class sets up a timer interrupt, and uses it to poll the front panel switches
#

class SwitchPoll:
    def init(self):
        self.last_tune_state = False
        self.last_ptt_state = False
        self.last_knob_state = False
        self.switch_timer = Timer()
        self.switch_timer.init(period=10, callback=self._interrupt_switch_timer)
        
    def _interrupt_switch_timer(self, timer_obj):
        micropython.schedule(self._switch_service, None)
    
    def _switch_service(self, dummy):
        cur_ptt_state = not pins.ctrl_button_ptt()
        cur_tune_state = not pins.ctrl_button_tune()
        cur_knob_state = not pins.ctrl_button_knob()
        # TUNE switch
        if self.last_tune_state != cur_tune_state:
            self.last_tune_state = cur_tune_state
            if cur_tune_state:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_TUNE_PRESSED)
                g.event.publish(event_data)
            else:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_TUNE_RELEASED)
                g.event.publish(event_data)
        # PTT Switch
        if self.last_ptt_state != cur_ptt_state:
            self.last_ptt_state = cur_ptt_state
            if cur_ptt_state:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_PTT_PRESSED)
                g.event.publish(event_data)
            else:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_PTT_RELEASED)
                g.event.publish(event_data)
        # Encoder Knob Switch
        if self.last_knob_state != cur_knob_state:
            self.last_knob_state = cur_knob_state
            if cur_knob_state:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_KNOB_PRESSED)
                g.event.publish(event_data)
            else:
                event_data = ev.EventData(ev.ET_SWITCHES, ev.EST_KNOB_RELEASED)
                g.event.publish(event_data)
        

  

                      
######################
# Class definitions  #
######################   

g.cal = ConfigRw()
switch_poller = SwitchPoll()
g.event = ev.Event()
g.vfo = vfo.Vfo()


##############################
# Emergency exception buffer #
##############################   

micropython.alloc_emergency_exception_buf(100)


######################
# Pin initialization #
######################


#
# I2C pins
#

pins.i2c_scl = Pin(13)
pins.i2c_sda = Pin(12)

#
# Define the Encoder pins
#

pins.encoder_i = Pin(14)
pins.encoder_q = Pin(15)


#
# Define the LCD Display Pins
#

pins.lcd_rs = Pin(16,Pin.OUT)
pins.lcd_e = Pin(17,Pin.OUT)
pins.lcd_d4 = Pin(18,Pin.OUT)
pins.lcd_d5 = Pin(19,Pin.OUT)
pins.lcd_d6 = Pin(20,Pin.OUT)
pins.lcd_d7 = Pin(21,Pin.OUT)
pins.lcd_backlight = Pin(22, Pin.OUT)

# Define the Control Signal Pins
pins.ctrl_button_ptt = Pin(2,Pin.IN, Pin.PULL_UP)
pins.ctrl_button_tune = Pin(3, Pin.IN, Pin.PULL_UP)
pins.ctrl_ptt_out = Pin(4, Pin.OUT)
pins.ctrl_tune_out = Pin(5, Pin.OUT)
pins.ctrl_mute_out = Pin(6, Pin.OUT)
pins.ctrl_agc_disable = Pin(7, Pin.OUT)
pins.ctrl_button_knob = Pin(8,Pin.IN, Pin.PULL_UP)
pins.ctrl_led = Pin(25, Pin.OUT)

#
# Read in the calibration constants
#


g.cal_data = g.cal.read(g.cal_file_dir, g.cal_defaults)

#
# Set default output state for control pins
#

pins.ctrl_led(0) # LED off\
pins.ctrl_ptt_out(0) # PTT OFF
pins.ctrl_tune_out(0) # Tune off
pins.ctrl_mute_out(0) # Mute off
pins.ctrl_agc_disable(0) # AGC on


#
# Initialize I2C
#

g.i2c = I2C(0, freq=100000, scl = pins.i2c_scl, sda = pins.i2c_sda)

#
# Create si5351 object
#

g.si5351 = clkgen.SI5351(g.i2c)

#
# Initialize the LCD driver
#

g.lcd = lcd.GpioLcd(pins.lcd_rs, pins.lcd_e, d4_pin = pins.lcd_d4,
                    d5_pin = pins.lcd_d5, d6_pin = pins.lcd_d6,
                    d7_pin = pins.lcd_d7, backlight_pin = pins.lcd_backlight)

#
# Safe mode check
#
# If the user holds down the tune button at power on
# this code will prevent further execution. This will
# prevent system lock up if something is wrong in the code
# that prevents Thonny from gaining control
#

if pins.ctrl_button_tune() == 0:
    g.lcd.move_to(0,0)
    g.lcd.putstr("** SAFE MODE **")
    while True:
        pass

#
# Initialize switch polling class

#

switch_poller.init()

#
# Initialize the encoder knob
#
g.encoder_q = list()
g.knob = knob.EncoderKnob(0, g.encoder_q, pins.encoder_i)


#
# Initialize the VFO
#
g.vfo.init({"40M":{"low_limit":7125000, "high_limit":7300000}})
        

#
# Main loop
#

last_gc_time = time.ticks_ms()
while True:
    # Service encoder knob queue
    try:
        direction = g.encoder_q.pop()
        if direction < 0:
            event_data = ev.EventData(ev.ET_ENCODER, ev.EST_KNOB_CCW)
        else:
            event_data = ev.EventData(ev.ET_ENCODER, ev.EST_KNOB_CW)
        g.event.publish(event_data)
                
    except IndexError:
        pass
    
    # garbage collect occasionally
    now = time.ticks_ms()
    if time.ticks_diff(now, last_gc_time) > 30000:
        last_gc_time = now
        gc.collect()
        print("Memory free: {}".format(gc.mem_free()))
    
    
    





