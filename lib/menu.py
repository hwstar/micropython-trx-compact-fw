import micropython
import lib.globals as g
import lib.constants as c
import lib.event as ev

# Note that all menu text is handled by the display module

class Menu:
    def init(self):
        self.in_menu_system = False
        g.event.add_subscriber(self.action, c.ET_ENCODER|c.ET_SWITCHES)
        self.group = 0
        self.entry = 0
    
       
    
    def active(self):
        return self.in_menu_system
    
    def action(self, event_data):
      
        # Knob switch long press enters/exits menu system
        if event_data.subtype == c.EST_KNOB_RELEASED_LONG:
            self.in_menu_system = not self.in_menu_system
            #print("In menu system: ", self.in_menu_system)
            if self.in_menu_system:
                # Write menu text
                self.group = 0
                self.entry = 0
            
                ed = ev.EventData(c.ET_DISPLAY, c.EST_DISPLAY_MENU_UPDATE, {"group": self.group, "entry": self.entry})
                g.event.publish(ed)
                # Display menu text
                ed = ev.EventData(c.ET_DISPLAY, c.EST_DISPLAY_MENU_ENTRY)
                g.event.publish(ed)
            else:
                # Switch back to normal operation
                ed = ev.EventData(c.ET_DISPLAY, c.EST_DISPLAY_MENU_EXIT)
                g.event.publish(ed)
                
                
                
            
                
            
      
    
    