#event class. every time you make an event one of these bad boys is born
class Event:
    def __init__(self, event_redis_key, start_unix, end_unix):
        self.event_redis_key = event_redis_key
        self.start_unix = start_unix
        self.end_unix = end_unix

    def __str__(self):
        return f"event_redis_key:{self.event_redis_key} start_unix:{self.start_unix} end_unix:{self.end_unix}"
    
    def get_key(self):
        return self.event_redis_key
    
    def get_start(self):
        return self.start_unix
    
    def get_end(self):
        return self.end_unix
    
    def is_same_event(self, new_event: "Event") -> bool:
        if not isinstance(new_event, Event): 
            raise TypeError(f"Expected new_event to be of type Event, got {type(new_event)}")
        
        return ( self.get_key() == new_event.get_key() 
                and self.get_start() == new_event.get_start() 
                and self.get_end() == new_event.get_end() ) #keep forgetting that i can just return the evaluation itself... well anyways