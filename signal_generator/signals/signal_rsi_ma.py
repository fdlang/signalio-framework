from ..interfaces.signal_generator_interface import ISignalGererator
from ..properties.signal_generator_properties import RsiMaCrossoverProperties
from .signal_ma_crossover import SignalMACrossover
from .signal_rsi import SignalRSI
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent


class RsiMaCrossover(ISignalGererator):
	
	def __init__(self, properties: RsiMaCrossoverProperties):

		self.properties = properties
		

	def generate_signal(self, data_event: DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		
		ma_rcossover = SignalMACrossover(properties=self.properties.ma_crossover)
		rsi = SignalRSI(self.properties.rsi)

		signal_event_ma = ma_rcossover.generate_signal(data_event, data_provider)
		signal_event_rsi = rsi.generate_signal(data_event, data_provider)

		if (signal_event_ma and signal_event_rsi
	  		and signal_event_ma.symbol == signal_event_rsi.symbol
			and signal_event_ma.signal == signal_event_rsi.signal
		):
			
			signal_event = SignalEvent(event_type=signal_event_ma.event_type,
										symbol=signal_event_ma.symbol,
										signal=signal_event_ma.signal,
										target_order="MARKET",
										target_price=signal_event_rsi.target_price,
										ref="RSI_MA",
										rsi=signal_event_rsi.rsi,
										timeframe=rsi.timeframe)
			
			return signal_event
		
		return None
		










