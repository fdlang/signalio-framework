from typing import Protocol
from events.events import DataEvent
from events.events import SignalEvent
from data_provider.data_provider import DataProvider


class ISignalGenerator(Protocol):

    def generate_signal(self, data_event:DataEvent, data_provider: DataProvider) -> SignalEvent | None:
        ...


    