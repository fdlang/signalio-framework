from ..interfaces.signal_generator_interface import ISignalGererator
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent
from queue import Queue


class SignalMACrossover(ISignalGererator):
	
	
	def __init__(self, event_queue: Queue, data: DataProvider, timeframe: str, fast_period: int, slow_period: int):

		self.event_queue = event_queue
		self.DATA = data

		self.timeframe = timeframe
		self.fast_period = fast_period if fast_period > 1 else 2
		self.slow_period = slow_period if slow_period > 2 else 3

		if self.fast_period >= self.slow_period:
			raise Exception(f"ERROR: el periodo rápido ({self.fast_period}) es mayor al periodo lento ({self.slow_period}) para el cálculo de las medias móviles")


	def _create_and_put_signal_event(self, symbol: str, signal: str, target_order: str, target_price: float, order_id: int) -> None:
		
		signal_event = SignalEvent(
				symbol=symbol,
				signal=signal,
				target_order=target_order,
				target_price=target_price,
				order_id=order_id,
			)

		# Pone el signal_event en la cola de eventos
		self.event_queue.put(signal_event)


	def generate_signal(self, data_event:DataEvent) -> None:
		
		symbol = data_event.symbol

		# Recupera datos para calcular las medias móviles
		bars = self.DATA.get_latest_closed_bars(symbol=symbol, timeframe=self.timeframe, num_bars=self.slow_period)


		if bars is not None and 'Close' in bars.columns and not bars.empty:
			bars['Close'] = bars['Close'].astype(float)

			# Calcula el valor de los indicadores
			fast_ma = bars['Close'][-self.fast_period:].mean()
			slow_ma = bars['Close'].mean()

			# Detecta una señal de compra
			if fast_ma > slow_ma:
				self._create_and_put_signal_event(
					symbol=symbol,
					signal="BUY",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					order_id=1, # Se debe cambiar por un id único para cada orden, ########## QUEDA PENDIENTE!!! ##########
				)

			# señal de venta
			elif slow_ma > fast_ma: 
				self._create_and_put_signal_event(
					symbol=symbol,
					signal="SELL",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					order_id=1, # Se debe cambiar por un id único para cada orden, ########## QUEDA PENDIENTE!!! ##########
				)
			else:
				# No hay señal de compra o venta
				pass
		
