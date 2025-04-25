from ..interfaces.signal_generator_interface import ISignalGererator
from ..properties.signal_generator_properties import MACrossoverProperties
from data_provider.data_provider import DataProvider
from events.events import DataEvent, SignalEvent


class SignalMACrossover(ISignalGererator):
	
	
	def __init__(self, properties: MACrossoverProperties):

		self.timeframe = properties.timeframe
		self.fast_period = properties.fast_period if properties.fast_period > 1 else 2
		self.slow_period = properties.slow_period if properties.slow_period > 2 else 3

		if self.fast_period >= self.slow_period:
			raise Exception(f"ERROR: el periodo rápido ({self.fast_period}) es mayor al periodo lento ({self.slow_period}) para el cálculo de las medias móviles")



	def generate_signal(self, data_event:DataEvent, data_provider: DataProvider) -> SignalEvent | None:
		
		symbol = data_event.symbol 

		# Recupera datos para calcular las medias móviles
		bars = data_provider.get_latest_closed_bars(symbol=symbol, timeframe=self.timeframe, num_bars=self.slow_period)


		if bars is not None and 'Close' in bars.columns and not bars.empty:
			bars['Close'] = bars['Close'].astype(float)

			# Calcula el valor de los indicadores
			fast_ma = bars['Close'][-self.fast_period:].mean()
			slow_ma = bars['Close'].mean()

			# Detecta una señal de compra
			if fast_ma > slow_ma:
				signal_event = SignalEvent(
					symbol=symbol,
					signal="BUY",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					order_id=1,
				)
				return signal_event

			# señal de venta
			elif slow_ma > fast_ma: 
				signal_event = SignalEvent(
					symbol=symbol,
					signal="SELL",
					target_order="MARKET",
					target_price=float(bars['Close'].iloc[-1]),
					order_id=2,
				)
				return signal_event
			else:
				# No hay señal de compra o venta
				return None
		
