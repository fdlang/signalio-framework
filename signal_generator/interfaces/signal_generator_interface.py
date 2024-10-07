from typing import Protocol
from events.events import DataEvent


class ISignalGererator(Protocol):

    def generate_signal(self, data_event:DataEvent) -> None:
        ...

