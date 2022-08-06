from machine import Pin
import micropython
import event as ev
import lib.globals as g
import lib.gpiopins as pins
import lib.gpio_lcd as lcd
import lib.si5351 as clkgen


class Vfo:
    
    # Set the frequncy of the clock generator outputs
    def _set_freq(self, freq: int, tx: int, mode: int):
        # Local copy of upper crystal filter 6dB corner frequency 
        cf_freq = g.cal_data["cf_frequency_hz"]
        # Diff freq must always be positive
        diff_freq = cf_freq - self.tuned_freq if cf_freq > self.tuned_freq else self.tuned_freq - cf_freq
        # Fconv is the conversion oscillator frequency
        fconv = self.tuned_freq + cf_freq if mode == 1 else diff_freq
        if tx:
            first_osc = cf_freq # First oscillator serves as balanced moduluator
            second_osc = fconv # Second oscillator serves as frequency converter
        else:
            first_osc = fconv # First oscillator serves as frequency converter
            second_osc = cf_freq # Second oscillator serves as BFO
        
        #print("first osc freq: {}".format(first_osc))
        #print("second osc freq: {}".format(second_osc))
        
        # SI5351 library needs frequencies specified in 100ths of hz.
        g.si5351.set_freq(clkgen.CLK0, first_osc * 100)
        g.si5351.set_freq(clkgen.CLK2, second_osc * 100)

        # Update frequency on display
        event_data = ev.EventData(ev.ET_DISPLAY, ev.EST_DISPLAY_UPDATE_FREQ, {"freq": freq})
        g.event.publish(event_data)
        
        # Update TX state if it has changed
        if tx != self.txstate:
            event_data = ev.EventData(ev.ET_DISPLAY, ev.EST_DISPLAY_UPDATE_TXSTATE, {"txstate": tx})
            self.txstate = tx
            g.event.publish(event_data)
        
        # Update mode if it has changed
        if mode != self.mode:
            event_data = ev.EventData(ev.ET_DISPLAY, ev.EST_DISPLAY_UPDATE_MODE, {"mode": mode})
            self.mode = mode
            g.event.publish(event_data)
            

    # Initialize the VFO 
    def init(self, band_table, tuned_freq: int = 7200000, mode: int = 0):
        self.band_table = band_table
        self.tuned_freq = tuned_freq
        self.mode = -1
        self.txstate = -1
        
        # Set up SI5351
        g.si5351.init(clkgen.CRYSTAL_LOAD_0PF, g.cal_data["xtal_freq_hz"], g.cal_data["si5351_correction_ppb"])
        
        # Tell the event handler we want to listen for switch and encoder events
        g.event.add_subscriber(self.action, ev.ET_ENCODER | ev.ET_SWITCHES)
        
        # Clock generator drive strength
        g.si5351.drive_strength(clkgen.CLK0, clkgen.DRIVE_8MA)
        g.si5351.drive_strength(clkgen.CLK1, clkgen.DRIVE_2MA)
        g.si5351.drive_strength(clkgen.CLK2, clkgen.DRIVE_8MA)
        
        # Clock generator output enable
        g.si5351.set_freq(clkgen.CLK0, 10000000)
        g.si5351.set_freq(clkgen.CLK2, 10000000)
        g.si5351.output_enable(clkgen.CLK0, True)
        g.si5351.output_enable(clkgen.CLK1, False)
        g.si5351.output_enable(clkgen.CLK2, True)
        
        
        # Set up the clock generator output frequencies and enable the outputs
        self._set_freq(self.tuned_freq, 0, mode)
        
        
    # This is called when the encoder knob is turned, or any switch is pressed or released   
    def action(self, event_obj: object):
        #print("Event Type: {} Subtype: {}".format(event_obj.type, event_obj.subtype))
        pass
        
        
        
       
    
    
    