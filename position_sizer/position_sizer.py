from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from .interfaces.position_sizer_interface import IPositionSizer


class PositionSizer(IPositionSizer):

    def __init__():
        pass

    def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
        pass
        