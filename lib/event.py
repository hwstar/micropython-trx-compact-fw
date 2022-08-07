#
# Event package
# This package handles subscribers wishing to listen to an event type,
# and allows messages to be published so that subscribers who are listening
# can receive those messages
#

# Event types
ET_ALL = const(0xFFFFFFFF)
ET_ENCODER = const(0x00000001)
ET_SWITCHES = const(0x00000002)
ET_VFO = const(0x00000004)
ET_DISPLAY = const(0x00000008)


# Event subtypes
EST_NONE = 0
EST_KNOB_CW = 1
EST_KNOB_CCW = 2
EST_KNOB_PRESSED = 3
EST_KNOB_RELEASED = 4
EST_KNOB_RELEASED_LONG = 5
EST_TUNE_PRESSED = 6
EST_TUNE_RELEASED = 7
EST_PTT_PRESSED = 8
EST_PTT_RELEASED = 9
EST_TX_TIMED_OUT_ENTRY = 10
EST_TX_TIMED_OUT_EXIT = 11
EST_DISPLAY_UPDATE_FREQ = 12
EST_DISPLAY_UPDATE_MODE = 13
EST_DISPLAY_UPDATE_TXSTATE = 14
EST_DISPLAY_UPDATE_TUNING_INCR = 15

# Protected class to keep track of subscriber info
class _EventSubscriber:
    def __init__(self, callback: callable, filter_bits: int):
        self.callback = callback
        self.filter_bits = filter_bits

# Event opject. The publisher creates one of these for every new event

class EventData:
    def __init__(self, event_type: int, event_subtype: int = 0, data: dict = None):
        self.type = event_type
        self.subtype = event_subtype
        self.data = data

# This class handles subscriber additions and message publication

class Event:
    def __init__(self):
        """ Constructor """
        self._subscribers = list()


    def add_subscriber(self,  callback: callable, filter_bits: int) -> None:
        """ Add a subscriber """
        new_subscriber = _EventSubscriber(callback, filter_bits)
        self._subscribers.append(new_subscriber)


    def publish(self, event_obj: EventData) -> None:
        """ Publish an event"""
        for subscriber in self._subscribers:
            # Check filter bits to see if this event is wanted by the subscriber
            if event_obj.type & subscriber.filter_bits:
                # The event is wanted
                subscriber.callback(event_obj)

    def get_subscriber_count(self) -> int:
        """ Return the number of subscribers for this event object"""
        return len(self._subscribers)











