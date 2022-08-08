import micropython
import event as ev
import lib.globals as g
import lib.constants as c
import lib.gpio_lcd as lcd

#
# Base class for display
#
# This class contains methods which are universal to any display type employed
#
#

class _DisplayBase:
    def init(self):
        pass
    
    def format_freq(self, freq_hz: int) -> str:
        # Format frequency integer as MM.KKKHHH string
        MHz,kHz = divmod(freq_hz,1000000)
        return "{:2d}.{:06d}".format(MHz, kHz)
    
    def format_mode(self, mode: int) -> str:
        # Format mode integer as LSB or USB string
        if mode == c.TXM_LSB:
            m_str = "LSB"
        elif mode == c.TXM_USB:
            m_str = "USB"
        else:
            m_str = "???"
        return m_str
    
    def format_tx_state(self, tx_state: int) -> str:
        # Format tx state integer as string
        if tx_state == c.TXS_RX:
            tx_str = "RX"
        elif tx_state == c.TXS_TX:
            tx_str = "TX"
        elif tx_state == c.TXS_TUNE:
            tx_str = "TU"
        elif tx_state == c.TXS_TIMEOUT:
            tx_str = "TO"
        else:
            tx_str = "??"
        return tx_str
    
    def format_tuning_incr(self, tuning_incr: int) -> str:
        # Format tuning increment integer as string
        kHz = tuning_incr // 1000
        if kHz:
            return "{:2d}k".format(kHz)
        else:
            return "{:3d}".format(tuning_incr)
        
        
    def format_agc_disable(self, agc_state: int) -> str:
        # Format agc state.
        return "AGC" if agc_state else "   "
        
 #
 # This class contains code specific to the type of
 # display being used. In this case it is a 1602 display
 #
 
class Display(_DisplayBase):
    def init(self):
        #
        # Initialization method.
        # Called from (x)main.py during initialization
        # This is purposely not a constructor in order
        # to have better control over the timing and order
        # of the initialization sequence.
        #
        super().init()
        g.event.add_subscriber(self.action, c.ET_DISPLAY)
        self.screens = dict()
        #
        # Create the "main" virtual screen which is the one used most of the time
        #
        self.current_screen = "main"
        self.virt_new_screen(self.current_screen)
        
        
    def virt_switch_screens(self, screen_name):
        #
        # Switch to another virtual screen
        #
        # Clears the text on the display, and
        # loads the display with any previous text,
        # if any
        
        if screen_name not in self.screens:
            return
        self.current_screen = screen_name
        # Clear the display
        g.lcd_clear()
        # Refresh the display with all of the fields which were stored previously
        for field in self.screen[screen_name]:
            g.move_to(field["x"], field["y"])
            g.putstr(field["text"])
            
    
    def virt_clear_screen(self, screen_name):
        #
        # Clear a virtual screen
        # This method clears a virtual screen
        # by emptying the dictionary of all the display items
        # If the virtual screen name is the same as the
        # current one being displayed, the physical display will be
        # cleared as well.
        #
        if screen_name not in self.screens:
            return
        self.screens[screen_name] = dict()
        # Write through if current screen is the same name
        if self.current_screen == screen_name:
            g.lcd.clear()
            
    def virt_new_screen(self, screen_name):
        # Defines a new screen name
        # If the screen name does not exist, create it here
        if screen_name not in self.screens:
            self.screens[screen_name] = dict()
    
    def virt_moveto_write(self, x, y, text, field_name, screen_name = "main"):
        #
        # Move to a position, and write a string
        #
        # Save a copy to restore later if the virtual screen is changed
        self.screens[screen_name][field_name] = {"x": x, "y": y, "text": text}
        
        # If the screen name is what is currently selected, write through to the display
        if self.current_screen == screen_name:
            g.lcd.move_to(x, y)
            g.lcd.putstr(text)
        
    def action(self, event_data):
        # Display events sent to this function
        # Frequency update
        if event_data.subtype == c.EST_DISPLAY_UPDATE_FREQ:
            freq = event_data.data["freq"] # Save a local copy to restore later if need be
            self.virt_moveto_write(0, 0, self.format_freq(freq), "freq")
       
        # Mode update
        elif event_data.subtype == c.EST_DISPLAY_UPDATE_MODE:
            mode = self.format_mode(event_data.data["mode"]) # Convert sideband to string and store locally
            self.virt_moveto_write(13, 0, mode, "mode")
        # TX State update
        elif event_data.subtype == c.EST_DISPLAY_UPDATE_TXSTATE: # Convert TX state to string
            tx_state = self.format_tx_state(event_data.data["txstate"])
            self.virt_moveto_write(10, 0, tx_state, "txstate")
        # Tuning increment update
        elif event_data.subtype == c.EST_DISPLAY_UPDATE_TUNING_INCR:
            tuning_incr = self.format_tuning_incr(event_data.data["incr"])
            self.virt_moveto_write(13, 1, tuning_incr, "incr")
        # AGC update
        elif event_data.subtype == c.EST_DISPLAY_UPDATE_AGC:
            agc_disable = self.format_agc_disable(event_data.data["agc"])
            self.virt_moveto_write(9, 1, agc_disable, "agc")
            
        
        
        
            
          
            
            
            
            
        
           
    
    