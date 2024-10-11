from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import FixedSizingProps


class RiskPctPositionSizer(IPositionSizer):

	def __init__(self, properties: FixedSizingProps):
		pass


	def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
		pass

   
