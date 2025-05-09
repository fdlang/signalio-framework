from ..interfaces.signal_generator_interface import ISignalGenerator
from ..properties.signal_generator_properties import RsiMaCrossoverProperties
from .signal_ma_crossover import SignalMACrossover
from .signal_rsi import SignalRSI
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent


class RsiMaCrossover(ISignalGenerator):
	
	def __init__(self, properties: RsiMaCrossoverProperties):

		self.properties = properties
		

	def _is_valid_combination(self, signal_event_ma: SignalEvent, signal_event_rsi: SignalEvent) -> bool:
	
		return (signal_event_ma is not None and signal_event_rsi is not None
				and signal_event_ma.symbol == signal_event_rsi.symbol
				and signal_event_ma.signal == "BUY")


	def generate_signal(self, data_event: DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		
		ma_crosover = SignalMACrossover(properties=self.properties.ma_crossover)
		rsi = SignalRSI(self.properties.rsi)

		signal_event_ma = ma_crosover.generate_signal(data_event, data_provider)
		signal_event_rsi = rsi.generate_signal(data_event, data_provider)

		if self._is_valid_combination(signal_event_ma, signal_event_rsi):
		
			signal_event = SignalEvent(event_type=signal_event_ma.event_type,
										symbol=signal_event_ma.symbol,
										signal=signal_event_rsi.signal,
										target_order="MARKET",
										target_price=signal_event_rsi.target_price,
										ref="RSI_MA",
										rsi=signal_event_rsi.rsi,
										timeframe=rsi.timeframe)
			
			return signal_event
		
		return None
		










