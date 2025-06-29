from src.signal_generator.interfaces.signal_generator_interface import ISignalGenerator
from src.signal_generator.properties.signal_generator_properties import RsiMaCrossoverProperties
from src.signal_generator.signals.signal_ma_crossover import SignalMACrossover
from src.signal_generator.signals.signal_rsi import SignalRSI
from src.data_provider.data_provider import DataProvider
from src.events.events import DataEvent, SignalEvent


class RsiMaCrossover(ISignalGenerator):
	
	def __init__(self, properties: RsiMaCrossoverProperties):

		self.properties = properties
		

	def _is_valid_combination(self, signal_event_ma: SignalEvent, signal_event_rsi: SignalEvent) -> bool:
	
		if isinstance(signal_event_ma, SignalEvent) and signal_event_ma.signal == "BUY" and \
			isinstance(signal_event_rsi, SignalEvent) and signal_event_rsi.signal == "BUY":
			return True
		
		elif isinstance(signal_event_ma, SignalEvent) and signal_event_ma.signal == "SELL" and \
			isinstance(signal_event_rsi, SignalEvent) and signal_event_rsi.signal == "SELL":
			return True
		
		return False
	

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
		










