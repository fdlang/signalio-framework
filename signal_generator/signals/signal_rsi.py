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
		'''
		Calcula el RSI (Relative Strength Index) de una serie de precios.
		El RSI es un indicador de momentum que mide la velocidad y el cambio de los movimientos de precios.
		El RSI oscila entre 0 y 100, y se utiliza para identificar condiciones de sobrecompra o sobreventa en un activo.
		Un RSI por encima de 70 indica que un activo está sobrecomprado, mientras que un RSI por debajo de 30 indica que está sobrevendido.
		'''
		deltas = np.diff(prices)

		# Calcula las ganancias y pérdidas
		gains = np.where(deltas > 0, deltas, 0)
		losses = np.where(deltas < 0, -deltas, 0) 

		# Inicialización del primer promedio
		avg_gain = np.mean(gains[-self.rsi_period:])
		avg_loss = np.mean(losses[-self.rsi_period:])

		# Suavizado de los valores de ganancia y pérdida (tipo Wilder)
		for i in range(self.rsi_period, len(prices)-1):  # Iteramos sobre el resto de las barras
			avg_gain = (avg_gain * (self.rsi_period - 1) + gains[i]) / self.rsi_period
			avg_loss = (avg_loss * (self.rsi_period - 1) + losses[i]) / self.rsi_period

		if avg_loss == 0:
			rsi = 100
		else:
			rs = avg_gain / avg_loss
			rsi = 100 - (100 / (1 + rs))

		return rsi

	

	def generate_signal(self, data_event:DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		'''
		Genera una señal de compra o venta en función del RSI.
		'''
		symbol = data_event.symbol 
		bars = data_provider.get_latest_closed_bars(symbol=symbol, timeframe=self.timeframe, num_bars=self.rsi_period + 1)
		rsi = self.compute_rsi(bars['Close'].astype(float))
		
		if bars is not None and 'Close' in bars.columns and not bars.empty:
			
			if rsi <= 30.0:
				signal_event = SignalEvent(
					symbol=symbol,
					signal="BUY",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					ref="RSI",
					rsi=rsi,
					timeframe=self.timeframe,
				)

				return signal_event

			elif rsi >= 70.0: 
				signal_event = SignalEvent(
					symbol=symbol,
					signal="SELL",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					ref="RSI",
					rsi=rsi,
					timeframe=self.timeframe
				)

				return signal_event
			else:
				
				return None


		
