from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._subscribers[event_type].append(handler)

    def emit(self, event_type, *args, **kwargs):
        for handler in self._subscribers.get(event_type, []):
            handler(*args, **kwargs)