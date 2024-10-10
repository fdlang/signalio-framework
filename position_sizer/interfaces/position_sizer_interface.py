from typing import Protocol
from events.events import SignalEvent


class IPôsitionSizer(Protocol):

    def size_position(self, signal_event: SignalEvent) -> None:
        ...
    

    