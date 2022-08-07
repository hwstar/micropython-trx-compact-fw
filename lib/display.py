import micropython
import event as ev
import lib.globals as g
import lib.constants as c
import lib.gpio_lcd as lcd

class _DisplayBase:
    def init(self):
        pass
    
    def format_freq(self, freq_hz: int) -> str:
        MHz,kHz = divmod(freq_hz,1000000)
        return "{:2d}.{:06d}".format(MHz, kHz)
    
    def format_mode(self, mode: int) -> str:
        if mode == c.TXM_LSB:
            m_str = "LSB"
        elif mode == c.TXM_USB:
            m_str = "USB"
        else:
            m_str = "???"
        return m_str
    
    def format_tx_state(self, tx_state: int) -> str:
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
        kHz = tuning_incr // 1000
        if kHz:
            return "{:2d}k".format(kHz)
        else:
            return "{:3d}".format(tuning_incr)
            
class Display(_DisplayBase):
    def init(self):
        super().init()
        g.event.add_subscriber(self.action, ev.ET_DISPLAY)
        self.screens = dict()
        self.current_screen = "main"
    
    def virt_switch_screens(screen_name):
        if screen_name not in self.screens:
            return
        self.current_screen = screen_name
        # Clear the display
        g.lcd_clear()
        # Refresh the display with all of the fields which were stored previously
        for field in self.screen[screen_name]:
            g.move_to(field["x"], field["y"])
            g.putstr(field["text"])
            
    
    def virt_clear_screen(screen_name):
        if screen_name not in self.screens:
            return
        self.screens[screen_name] = dict()
        # Write through if current screen is the same name
        if self.current_screen == screen_name:
            g.lcd.clear()
         
        
    def virt_moveto_write(self, x, y, text, field_name, screen_name):
        
        # If the virtual screen name does not exist, create it here
        if screen_name not in self.screens:
            self.screens[screen_name] = dict()
        
        # Save a copy to restore later if the virtual screen is changed
        self.screens[screen_name][field_name] = {"x": x, "y": y, "text": text}
        
        # If the screen name is what is currently selected, write through to the display
        if self.current_screen == screen_name:
            g.lcd.move_to(x, y)
            g.lcd.putstr(text)
        
       
        
    # Display events are sent to this function
    def action(self, event_data):
        # Frequency update
        if event_data.subtype == ev.EST_DISPLAY_UPDATE_FREQ:
            freq = event_data.data["freq"] # Save a local copy to restore later if need be
            self.virt_moveto_write(0, 0, self.format_freq(freq), "freq", "main")
       
        # Mode update
        elif event_data.subtype == ev.EST_DISPLAY_UPDATE_MODE:
            mode = self.format_mode(event_data.data["mode"]) # Convert sideband to string and store locally
            self.virt_moveto_write(13, 0, mode, "mode", "main")
        # TX State update
        elif event_data.subtype == ev.EST_DISPLAY_UPDATE_TXSTATE: # Convert TX state to string
            tx_state = self.format_tx_state(event_data.data["txstate"])
            self.virt_moveto_write(10, 0, tx_state, "txstate", "main")
        # Tuning increment update
        elif event_data.subtype == ev.EST_DISPLAY_UPDATE_TUNING_INCR:
            tuning_incr = self.format_tuning_incr(event_data.data["incr"])
            self.virt_moveto_write(13, 1, tuning_incr, "tincr", "main")
          
            
            
            
            
        
           
    
    