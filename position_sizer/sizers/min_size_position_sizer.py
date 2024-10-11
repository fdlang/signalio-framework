from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPôsitionSizer


class MinSizePositionSizer(IPôsitionSizer):

    def size_position(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
        
        