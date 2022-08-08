#
# Event package
# This package handles subscribers wishing to listen to an event type,
# and allows messages to be published so that subscribers who are listening
# can receive those messages
#

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











