#event class. every time you make an event one of these bad boys is born
class Event:
    def __init__(self, event_redis_key, start_unix, end_unix):
        self.event_redis_key = event_redis_key
        self.start_unix = start_unix
        self.end_unix = end_unix