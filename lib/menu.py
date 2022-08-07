import micropython
import lib.globals as g
import lib.constants as c
import lib.event as ev

class Menu:
    def init(self):
        self.in_menu_system = False
        g.event.add_subscriber(self.action, ev.ET_ENCODER|ev.ET_SWITCHES)
        pass
    
    def active(self):
        return self.in_menu_system
    
    def action(self, event_data):
        # Knob switch long press enters/exits menu system
        if event_data.subtype == ev.EST_KNOB_RELEASED_LONG:
            self.in_menu_system = not self.in_menu_system
            print("In menu system: ", self.in_menu_system)
      
    
    