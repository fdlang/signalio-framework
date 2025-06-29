from src.signal_generator.interfaces.signal_generator_interface import ISignalGenerator
from src.data_provider.data_provider import DataProvider
from src.events.events import DataEvent, SignalEvent
from src.signal_generator.properties.signal_generator_properties import RSIProperties

import pandas as pd
import numpy as np


class SignalRSI(ISignalGenerator):
	
	
	def __init__(self, properties: RSIProperties):
		self.timeframe = properties.timeframe
		self.rsi_period = max(properties.rsi_period, 2)  # Asegura un valor mínimo de 2

		if 0 <= properties.rsi_upper <= 100:
			self.rsi_upper = properties.rsi_upper
		else:
			self.rsi_upper = 70

		if 0 <= properties.rsi_lower <= 100:
			self.rsi_lower = properties.rsi_lower
		else:
			self.rsi_lower = 30

		if self.rsi_lower >= self.rsi_upper:
			raise ValueError(
				f"ERROR: El límite inferior del RSI ({self.rsi_lower}) no puede ser mayor o igual al límite superior ({self.rsi_upper})."
			)


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
			
			if rsi <= self.rsi_lower:
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

			elif rsi >= self.rsi_upper: 
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


		
