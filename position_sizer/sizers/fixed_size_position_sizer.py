from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import FixedSizingProps


class FixedSizePositionSizer(IPositionSizer):

    def __init__(self, properties: FixedSizingProps):
        self.fixed_volume = properties.volume
    

    def size_position(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:

        # Devuelve el tamaño de posición fija 
        return self.fixed_volume
