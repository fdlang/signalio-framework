from ..interfaces.signal_generator_interface import ISignalGererator
from ..properties.signal_generator_properties import MACrossoverProperties, RSIProperties, RsiMaCrossoverProperties
from data_provider.data_provider import DataProvider
from .signal_ma_crossover import SignalMACrossover
from .signal_rsi import SignalRSI
from events.events import DataEvent, SignalEvent

class RsiMaCrossover(ISignalGererator):
	
	def __init__(self, properties: RsiMaCrossoverProperties):

		self.properties = properties

	def generate_signal(self, data_event: DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		
		ma_rcossover = SignalMACrossover(properties=self.properties.ma_crossover)
		rsi = SignalRSI(self.properties.rsi)

		print(f"######################################{ma_rcossover}") 

		return None
		










