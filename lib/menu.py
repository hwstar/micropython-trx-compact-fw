import micropython
import lib.globals as g
import lib.constants as c
import lib.event as ev

# Note that all menu text is handled by the display module




class Menu:
    def __init__(self):
        #
        # Initialize menu tree
        #
        self.back = {"type": "pop"}
        
        self.lsb_leaf = {"type": "leaf", "handler": lambda: self._publish_message(c.ET_VFO, c.EST_VFO_MODE_LSB)}
        self.usb_leaf = {"type": "leaf", "handler": lambda: self._publish_message(c.ET_VFO, c.EST_VFO_MODE_USB)}
        
        self.agc_on_leaf = {"type": "leaf", "handler": lambda: self._publish_message(c.ET_VFO, c.EST_VFO_AGC_ENABLE)}
        self.agc_off_leaf = {"type": "leaf", "handler": lambda: self._publish_message(c.ET_VFO, c.EST_VFO_AGC_DISABLE)}
        
        self.emission_menu = {"type": "node", "group": 1, "entries": [self.lsb_leaf, self.usb_leaf, self.back]}
        self.agc_menu = {"type": "node", "group": 2, "entries": [self.agc_on_leaf, self.agc_off_leaf, self.back]}
        
        self.menu_root = {"type": "node", "group": 0, "entries": [self.emission_menu, self.agc_menu]}
        
        #
        # Initialize other variables
        #
        
        self.in_menu_system = False
        self.menu_stack = list()
        self.entry = 0
        self.num_emtries = 0
        
    
    
    def init(self):
        # Subscribe to the encoder and switch events
        g.event.add_subscriber(self.action, c.ET_ENCODER|c.ET_SWITCHES)
 
  
    
    def _push(self, menu: object):
        # Push a menu item onto the stack
        self.menu_stack.append(menu)
    
    def _pop(self) -> object :
        # pop menu item from stack
        # If nothing is in the stack, return the root menu
        try:
            return self.menu_stack.pop()
        except IndexError:
            return self.menu_root
        
    def _publish_message(self, message_type: int, message_subtype: int, message_data = None):
        # Publish a message
        ed = ev.EventData(message_type, message_subtype, message_data)
        g.event.publish(ed)
    
    def _update(self):
        # Update display if we have a node
        if self.current_menu_level["type"] == "node":
            self._publish_message(c.ET_DISPLAY, c.EST_DISPLAY_MENU_UPDATE, {"group": self.current_menu_level["group"], "entry": self.entry})
          
       
    def active(self):
        # Return true if the menu system is active
        return self.in_menu_system      
    
    
    
    def action(self, event_data):
        # Act on a a switch or encoder event
        
        # Knob switch long press enters/exits menu system
        if event_data.subtype == c.EST_KNOB_RELEASED_LONG:
            self.in_menu_system = not self.in_menu_system
            if self.in_menu_system:
                self.menu_stack = list()
                self.current_menu_level = self.menu_root
                # Set number of entries for the root menu
                self.num_entries = len(self.menu_root["entries"])
                self.entry = 0
                # Write menu text
                self._update()
                # Display menu text
                ed = ev.EventData(c.ET_DISPLAY, c.EST_DISPLAY_MENU_ENTRY)
                g.event.publish(ed)
            else:
                # Switch back to normal operation
                ed = ev.EventData(c.ET_DISPLAY, c.EST_DISPLAY_MENU_EXIT)
                g.event.publish(ed)
                
        # Short knob press
        elif event_data.subtype == c.EST_KNOB_RELEASED:
            # Select the current item
            if self.current_menu_level["type"] == "node":
                next_menu_level = self.current_menu_level["entries"][self.entry]
          
                # Look at the next menu level
                if next_menu_level["type"] == "pop":
                    self.current_menu_level = self._pop()
                    self.num_entries = len(self.current_menu_level["entries"])
                    self.entry = 0
                    self._update()
                               
                elif next_menu_level["type"] == "leaf":
                    handler = next_menu_level["handler"]
                    if handler:
                        handler()
                    self.current_menu_level = self._pop()
                    self.entry = 0
                    self.num_entries = len(self.current_menu_level["entries"])
                    self._update()
                    
                elif next_menu_level["type"] == "node":
                    self._push(self.current_menu_level)
                    self.current_menu_level = self.current_menu_level["entries"][self.entry]
                    self.entry = 0
                    self.num_entries = len(self.current_menu_level["entries"])
                    self._update()
            
        
        # Encoder CW
        elif event_data.subtype == c.EST_KNOB_MENU_CW:
            # Advance to the next entry
            if self.current_menu_level["type"] == "node":
                self.entry = self.entry + 1
                if self.entry >= self.num_entries:
                    self.entry = 0
                # Write menu text
                self._update()
            
        # Encoder CCW
        elif event_data.subtype == c.EST_KNOB_MENU_CCW:
            # Retreat to the previouse entry
              if self.current_menu_level["type"] == "node":
                self.entry = self.entry - 1
                if self.entry < 0:
                    self.entry = self.num_entries - 1
                # Write menu text
                self._update()
            
        
       
        
                
            
                
            
      
    
    