from typing import Protocol
from events.events import SignalEvent
from data_provider.data_provider import DataProvider


class IPôsitionSizer(Protocol):

    def size_position(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
        ...
    



