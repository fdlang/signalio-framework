from ..interfaces.signal_generator_interface import ISignalGererator
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent

import pandas as pd
import numpy as np
from queue import Queue



class SignalMACrossover(ISignalGererator):
	
	
	def __init__(self, event_queue: Queue, data: DataProvider, timeframe: str, rsi_period: int, rsi_upper: float, rsi_lower: float):

		self.event_queue = event_queue
		self.DATA = data

		self.timeframe = timeframe
		self.rsi_period = rsi_period if rsi_period > 2 else 2 # El periodo debe ser mayor a 2 para evitar errores en el cálculo del RSI
		self.rsi_upper = rsi_upper if rsi_upper < 100 else 100 # El límite superior del RSI no puede ser mayor a 100
		
		if rsi_upper > 100 or rsi_upper < 0:
			self.rsi_upper = 70 
		else:
			self.rsi_upper = rsi_upper

		if rsi_lower > 100 or rsi_lower < 0:
			self.rsi_lower = 30 
		else:
			self.rsi_lower = rsi_lower

		if self.rsi_lower >= self.rsi_upper:
			raise Exception(f"ERROR: El límite inferior del RSI ({self.rsi_lower}) no puede ser mayor o igual al límite superior ({self.rsi_upper}).")


	def compute_rsi(self, prices: pd.series) -> float:

		deltas = np.diff(prices)
		gains = np.where(deltas > 0, deltas, 0)
		losses = np.where(deltas < 0, -deltas, 0) # Convertimos las pérdidas a valores positivos
		
		average_gain = np.mean(gains[-self.rsi_period:])
		average_loss = np.mean(losses[-self.rsi_period:])

		# Aplicamos la formula RSI: rsi = 100 - (100 / (1 + (average_gain / average_loss)))
		rs = average_gain / average_loss if average_loss > 0 else 0
		rsi = 100 - (100 / (1 + rs))

		return rsi


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
					order_id=2, # Se debe cambiar por un id único para cada orden, ########## QUEDA PENDIENTE!!! ##########
				)
			else:
				# No hay señal de compra o venta
				pass
		
