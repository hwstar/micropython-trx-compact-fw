import micropython
import event as ev
import lib.globals as g
import lib.constants as c
import lib.gpio_lcd as lcd


DISPLAY_LINE_LENGTH = 16


#
# Base class for display
#
# This class contains methods which are universal to any display type employed
#
# All text strings displayed are stored in this module. This keeps them all in one place.
# None of the other modules deal with text strings which are displayed on the display.
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
        # Create the "menu" and "main" virtual screens. 
        #
        self.current_screen = "main"
        self.virt_new_screen("menu")
        self.virt_new_screen(self.current_screen)
        
        #
        # Text for the menu is stored in this
        # list of lists. The menu module accesses
        # these strings by group and entry indexes
        #
        self.menutext = [
            ["**Main Menu**",["USB/LSB", "AGC ON/OFF"]], # Group 0
            ["**LSB/USB**",["LSB", "USB","^BACK"]], # Group 1
            ["**AGC**",["ON", "OFF", "^BACK"]] # Group 2
            ]
        
        
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
        g.lcd.clear()
        # Refresh the display with all of the fields which were stored previously
        screen = self.screens[screen_name]
        for name, field in screen.items():
            g.lcd.move_to(field["x"], field["y"])
            g.lcd.putstr(field["text"])
            
    
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
        # Clear the previous X,Y and Text data
        self.screens[screen_name] = dict()
        # Write through if current screen is the same name
        if self.current_screen == screen_name:
            g.lcd.clear()
            
    def virt_new_screen(self, screen_name):
        # Defines a new screen name
        #
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
        # Main menu entry
        elif event_data.subtype == c.EST_DISPLAY_MENU_ENTRY:
            self.virt_switch_screens("menu")
        elif event_data.subtype == c.EST_DISPLAY_MENU_EXIT:
            self.virt_switch_screens("main")
        # Update the menu screen
        elif event_data.subtype == c.EST_DISPLAY_MENU_UPDATE:
            mli = event_data.data["group"]
            mei = event_data.data["entry"]
            # Pad the menu group so it appears in the center
            ml_format ="{:^"+"{}".format(DISPLAY_LINE_LENGTH)+"s}"
            ml_str = ml_format.format(self.menutext[mli][0])
            # Pad the menu entry so it is left justified
            me_format ="{:<"+"{}".format(DISPLAY_LINE_LENGTH)+"s}"
            me_str = me_format.format(self.menutext[mli][1][mei])
            self.virt_moveto_write(0, 0, ml_str, "group", "menu")
            self.virt_moveto_write(0, 1, me_str, "entry", "menu")
            
            
            
            
            
            
        
        
        
            
          
            
            
            
            
        
           
    
    