from typing import Protocol
from src.events.events import DataEvent
from src.events.events import SignalEvent
from src.data_provider.data_provider import DataProvider


class ISignalGenerator(Protocol):

    def generate_signal(self, data_event:DataEvent, data_provider: DataProvider) -> SignalEvent | None:
        ...


    