from binance.client import Client
from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import RiskPctSizingProps


class RiskPctPositionSizer(IPositionSizer):

	def __init__(self, properties: RiskPctSizingProps):
		self.risk_pct = properties.risk_pct


	def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider, asset_buy_unid: float	) -> float:
		
		# Resiva que el riesgo se positivo
		if self.risk_pct <= 0.0:
			print(f"ERROR (RiskPctPositionSizer): El porcentaje de riesgo introducido {self.risk_pct} no es válido.")
			return 0.0

		# Revisa que el stop loss  sea != 0
		if signal_event.sl <= 0.0:
			print(f"ERROR (RiskPctPositionSizer): El valor del Stop Loss (SL): {self.risk_pct} no es válido.")
			return 0.0 

		# Accede a la información del símbolo (para poder calcular el riesgo)
		symbol_info = Client().get_symbol_info(signal_event.symbol)

		# Recupera el precio de entrada estimado:
		# Si es una orden de mercasdo
		if signal_event.target_order == "MARKET":

			# obtiene el últimno precio disponible en el mercado (ask o bid)
			last_tick = data_provider.get_latest_tick(signal_event.symbol)
			bid_ask = data_provider.get_bid_ask(signal_event.symbol)
			
			last_tick_price = last_tick[0]['price']

			if bid_ask:
				bid = bid_ask['bid']
				ask = bid_ask['ask']

				if last_tick_price == bid and signal_event.signal == "SELL":
					entry_price = bid
				elif last_tick_price == ask and signal_event.signal == "BUY":
					entry_price = ask
			else:
				print(f"ERROR (RiskPctPositionSizer): No existe valor en bid o ask: {bid_ask}")

		# si es una orden pendiente (limit o stop)
		else:
			# Coge el precio del propio signal event
			entry_price = signal_event.target_price

		# Consigue los valores que faltan para los cálculos
		equity = data_provider.get_account_balance_usdt()		# Saldo de la cuenta
		volume_step = symbol_info['filters'][1]['stepSize']		# Cambio mínimo de volumen
		tick_size = symbol_info['filters'][0]['tickSize'] 		# Cambio mínimo de precio 
		account_ccy = "USDT"									# Divisa de la cuenta
		symbol_profit_ccy = symbol_info['quoteAsset'] 			# Divisa del asset
		asset_unid = asset_buy_unid								# Unidades de la divisa que se quiere comprar
		
		# Cálculos auxiliares
		tick_value_profit_ccy = asset_unid * tick_size			# Cántidad ganada o perdida por cada tick

		# Conviertick el tick value en profit ccy del symbolo a la divisa de la cuenta
		tick_value_account_ccy = 5

	    # Cálculo del tamaño de la posición
		price_distance_in_integer_ticksizes = int(abs(entry_price - signal_event.sl) / tick_size)
		monetary_risk = equity * self.risk_pct	
		volume = monetary_risk / (price_distance_in_integer_ticksizes * tick_value_account_ccy)
		volume = round(volume / volume_step) * volume_step

		return volume
		
