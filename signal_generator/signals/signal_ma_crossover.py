from ..interfaces.signal_generator_interface import ISignalGererator
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent
from queue import Queue
import pandas as pd


class SignalMACrossover(ISignalGererator):
	
	
	def __init__(self, event_queue: Queue, data: DataProvider, timeframe: str, fast_period: int, slow_period: int):

		self.event_queue = event_queue
		self.DATA = data
		self.timeframe = timeframe
		self.fast_period = fast_period if fast_period > 1 else 2
		self.slow_period = slow_period if slow_period > 2 else 3

		if self.fast_period >= self.slow_period:
			raise Exception(f"ERROR: el periodo rápido ({self.fast_period}) es mayor al periodo lento ({self.slow_period}) para el cálculo de las medias móviles")


	def _create_and_put_signal_event(self, symbol: str, signal: str, target_order: str, target_price: float, order_id: int, sl: float, tp: float) -> None:
		
		signal_event = SignalEvent(
				symbol=symbol,
				signal=signal,
				target_order=target_order,
				target_price=target_price,
				order_id=order_id,
				sl=sl,
				tp=tp
			)

		# Pone el signal_event en la cola de eventos
		self.event_queue.put(signal_event)


	def generate_signal(self, data_event:DataEvent) -> None:
		
		symbol = data_event.symbol

		# Recupera datos para calcular las medias móviles
		bars = self.DATA.get_latest_closed_bars(symbol=symbol, timeframe=self.timeframe, num_bars=self.slow_period)
		
		if bars is not None and 'Close' in bars.columns and not bars.empty:
			bars['Close'] = pd.to_numeric(bars['Close'])

			# Calcula el valor de los indicadores
			fast_ma = bars['Close'][-self.fast_period:].mean()
			slow_ma = bars['Close'].mean()

			# Detecta una señal de compra
			if fast_ma > slow_ma:
				signal = "BUY"

			# señal de venta
			elif slow_ma > fast_ma: 
				signal = "SELL"
			else:
				signal = ""
			
			if signal != "":
				self._create_and_put_signal_event(
					symbol=symbol,
					signal=signal,
					target_order="MARKET",
					target_price=0.0,
					order_id=1234,
					sl=155.0,
					tp=130.0
				)

