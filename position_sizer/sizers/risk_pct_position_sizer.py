from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer
from ..properties.position_sizer_properties import RiskPctSizingProps


class RiskPctPositionSizer(IPositionSizer):

	def __init__(self, properties: RiskPctSizingProps):
		self.rick_pct = properties.risk_pct


	def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
		
		# Resiva que el riesgo se positivo
		if self.rick_pct <= 0.0:
			print(f"ERROR (RiskPctPositionSizer): El porcentaje de riesgo introducido {self.rick_pct} no es válido.")
			return 0.0

		# Revisa que el stop loss  sea != 0
		if signal_event.sl <= 0.0:
			print(f"ERROR (RiskPctPositionSizer): El valor del Stop Loss (SL): {self.rick_pct} no es válido.")
			return 0.0 

		# Accede a la informacion de la cuenta
		account_info = data_provider.client.get_account()

		# Accede a la información del símbolo (para poder calcular el riesgo)
		symbol_info = data_provider.get_symbol_info(signal_event.symbol)

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

		# si es una orden pendiente (limit o stop)
		else:
			# Coge el precio del propio signal event
			entry_price = signal_event.target_price

		# Consigue los valores que faltan para los calculos
		equity = 0.0 
		volume_step = symbol_info['filters'][1]['stepSize']	# Cambio mínimo de volumen
		tickSize = symbol_info['filters'][0]['tickSize'] 		# Cambio mínimo de precio 
		account_ccy = symbol_info['quoteAsset'] 				# Divisa de la cuenta
		
		for asset in account_info['balances']:
			free_balance = float(asset['free']) # saldo disponible
			locked_balance = float(asset['locked']) # saldo bloqueado
			equity += free_balance + locked_balance

		
