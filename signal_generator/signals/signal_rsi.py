from ..interfaces.signal_generator_interface import ISignalGererator
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent
from ..properties.signal_generator_properties import RSIProperties

import pandas as pd
import numpy as np


class SignalRSI(ISignalGererator):
	
	
	def __init__(self, properties: RSIProperties):

		self.timeframe = properties.timeframe
		self.rsi_period = properties.rsi_period if properties.rsi_period > 2 else 2 # El periodo debe ser mayor a 2 para evitar errores en el cálculo del RSI
		self.rsi_upper = properties.rsi_upper if properties.rsi_upper < 100 else 100 # El límite superior del RSI no puede ser mayor a 100
		
		if properties.rsi_upper > 100 or properties.rsi_upper < 0:
			self.rsi_upper = 70 
		else:
			self.rsi_upper = properties.rsi_upper

		if properties.rsi_lower > 100 or properties.rsi_lower < 0:
			self.rsi_lower = 30 
		else:
			self.rsi_lower = properties.rsi_lower

		if self.rsi_lower >= self.rsi_upper:
			raise Exception(f"ERROR: El límite inferior del RSI ({self.rsi_lower}) no puede ser mayor o igual al límite superior ({self.rsi_upper}).")


	def compute_rsi(self, prices: pd.Series) -> float:
		
		prices_array = prices.to_numpy()
		deltas = np.diff(prices_array)

		gains = np.where(deltas > 0, deltas, 0)
		losses = np.where(deltas < 0, -deltas, 0)

		avg_gain = np.mean(gains[:self.rsi_period])
		avg_loss = np.mean(losses[:self.rsi_period])

		# Suavizado exponencial (tipo Wilder) sobre los siguientes valores
		for i in range(self.rsi_period, len(gains)):
			avg_gain = (avg_gain * (self.rsi_period - 1) + gains[i]) / self.rsi_period
			avg_loss = (avg_loss * (self.rsi_period - 1) + losses[i]) / self.rsi_period

		# RSI final basado en el último promedio suavizado
		if avg_loss == 0:
			rsi = 100
		else:
			rs = avg_gain / avg_loss
			rsi = 100 - (100 / (1 + rs))

		return rsi
	

	def generate_signal(self, data_event:DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		
		symbol = data_event.symbol 

		# Recupera los datos necesarios para el cálculo del RSI		
		bars = data_provider.get_latest_closed_bars(symbol=symbol, timeframe=self.timeframe, num_bars=self.rsi_period + 1)

		# Calcula el RSI de las últimas velas
		rsi = self.compute_rsi(bars['Close'].astype(float))
		
		if bars is not None and 'Close' in bars.columns and not bars.empty:
			
			# señal de compra
			if rsi <= 30:
				signal_event = SignalEvent(
					symbol=symbol,
					signal="BUY",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					ref="RSI",
					rsi=rsi,
				)

				return signal_event

			# señal de venta
			elif rsi >= 70: 
				signal_event = SignalEvent(
					symbol=symbol,
					signal="SELL",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					ref="RSI",
					rsi=rsi,
				)

				return signal_event
			else:
				# No hay señal de compra o venta
				return None


		
