from .interfaces.signal_generator_interface import ISignalGererator
from .properties.signal_generator_properties import BaseSignalProps, MACrossoverProperties, RSIProperties
from .signals.signal_ma_crossover import SignalMACrossover
from .signals.signal_rsi import SignalRSI
from events.events import DataEvent, SignalEvent
from data_provider.data_provider import DataProvider

import queue


class SignalGenerator(ISignalGererator):
	def __init__(self, event_queue: queue, data_provider: DataProvider, signal_properties: BaseSignalProps) -> None:
		
		self.event_queue = event_queue
		self.data_provider = data_provider
		self.signal_generator_method = self._get_signal_generator_method(signal_properties)


	def _get_signal_generator_method(self, signal_props: BaseSignalProps) -> ISignalGererator:
	
		if isinstance(signal_props, MACrossoverProperties):
			return SignalMACrossover(properties=signal_props)
		
		elif isinstance(signal_props, RSIProperties):
			return SignalRSI(properties=signal_props)

		else:
			raise Exception(f'ERROR: No se ha definido un método de señal para las propiedades {signal_props}')
							

	def generate_signal(self, data_event: DataEvent) -> None:
		
		signal_event = self.signal_generator_method.generate_signal(data_event, self.data_provider)

		if signal_event is not None:
			self.event_queue.put(signal_event)

	

	def _create_and_put_signal_event(self, signal_event) -> None:
		
		# Pone el signal_event en la cola de evetos
		pass
		
	
