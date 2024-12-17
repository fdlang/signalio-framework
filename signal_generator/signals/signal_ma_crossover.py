from ..interfaces.signal_generator_interface import ISignalGererator
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent
from portfolio.portfolio import Portfolio
from order_executor.spot_order_executor import SpotOrderExecutor
from queue import Queue
import pandas as pd


class SignalMACrossover(ISignalGererator):
	
	
	def __init__(self, event_queue: Queue, data: DataProvider, portfolio: Portfolio, spot_order_executer: SpotOrderExecutor, timeframe: str, fast_period: int, slow_period: int):

		self.event_queue = event_queue
		self.DATA = data
		self.PORTFOLIO = portfolio
		self.SPOT_ORDER_EXECUTOR = spot_order_executer

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
		
		# Recupera las posiciones abiertas por esta estrategia en el simbolo donde se ha tenido el Data event
		open_position = self.PORTFOLIO.get_number_of_strategy_open_position_by_symbol(symbol)

		if bars is not None and 'Close' in bars.columns and not bars.empty:
			bars['Close'] = pd.to_numeric(bars['Close'])

			# Calcula el valor de los indicadores
			fast_ma = bars['Close'][-self.fast_period:].mean()
			slow_ma = bars['Close'].mean()

			# Detecta una señal de compra
			if open_position['LONG'] == 0 and fast_ma > slow_ma:
				if open_position['SHORT'] > 0:
					self.SPOT_ORDER_EXECUTOR.cancel_pending_order_by_symbol(symbol)
				signal = "BUY"

			# señal de venta
			elif open_position['SHORT'] == 0 and slow_ma > fast_ma: 
				if open_position['LONG'] > 0:
					self.SPOT_ORDER_EXECUTOR.cancel_pending_order_by_symbol(symbol)
				signal = "SELL"
			else:
				signal = ""
			
			if signal != "":
				self._create_and_put_signal_event(
					symbol=symbol,
					signal=signal,
					target_order="MARKET",
					target_price=0.0,
					order_id=self.PORTFOLIO.order_id,
					sl=0.0,
					tp=0.0
				)

