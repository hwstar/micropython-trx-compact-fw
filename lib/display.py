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
    
        
class Display(_DisplayBase):
    def init(self):
        super().init()
        self.freq = 0
        self.mode = ""
        self.tx_state = ""
        g.event.add_subscriber(self.action, ev.ET_DISPLAY)
        
    # Display events are sent to this function
    def action(self, event_data):
        # Frequency update
    
        if event_data.subtype == ev.EST_DISPLAY_UPDATE_FREQ:
            self.freq = event_data.data["freq"] # Save a local copy to restore later if need be
            g.lcd.move_to(0,0)
            g.lcd.putstr(self.format_freq(self.freq))
        # Mode update
        elif event_data.subtype == ev.EST_DISPLAY_UPDATE_MODE:
            self.mode = self.format_mode(event_data.data["mode"]) # Convert sideband to string and store locally
            g.lcd.move_to(13,0)
            g.lcd.putstr(self.mode)
        elif event_data.subtype == ev.EST_DISPLAY_UPDATE_TXSTATE: # Convert TX state to string
            self.tx_state = self.format_tx_state(event_data.data["txstate"])
            g.lcd.move_to(10,0)
            g.lcd.putstr(self.tx_state)
            
            
            
            
        
           
    
    