from binance.client import Client
from datetime import datetime, timezone
from events.events import SignalEvent


class Utils():

	def __init__(self):
		pass

	@staticmethod
	def convert_currency_amount_to_another_currency(amount: float, from_ccy: str, to_ccy: str) -> float:

		all_fx_symbol = set()
		exchange_info = Client().get_exchange_info()

		for symbol_info in exchange_info['symbols']:
			all_fx_symbol.add(symbol_info['symbol'])

		from_ccy = from_ccy.upper()
		to_ccy = to_ccy.upper()

		fx_symbol_candidates = [symbol for symbol in all_fx_symbol if from_ccy in symbol and to_ccy in symbol]
		
		if not fx_symbol_candidates:
			raise ValueError(f"No se encontraron símbolos de cambio para {from_ccy} a {to_ccy}")

		fx_symbol = fx_symbol_candidates[0]

		try:
			tick = Client().get_ticker(symbol=fx_symbol)

			if tick is None:
				raise ValueError(f"El símbolo {fx_symbol} no está disponible en la plataforma Binance.")

			last_price = float(tick['bidPrice'])

			# Determinar la base del símbolo
			if fx_symbol.endswith('USDT'):
				fx_symbol_base = fx_symbol[:-4]  
			elif fx_symbol.endswith('BTC'):
				fx_symbol_base = fx_symbol[:-3]  
			else:
				raise ValueError(f"El símbolo {fx_symbol} no es válido.")

			# Convierte la cantidad de la divisa origen a la divisa destino
			if fx_symbol_base == to_ccy:
				convert_amount = amount * last_price  # Convierte a la divisa base
			else:
				convert_amount = amount / last_price  # Convierte a USDT o BTC

			return convert_amount

		except Exception as e:
			print(f"ERROR: No se pudo recuperar el último símbolo {fx_symbol}. Exception: {e}")
			return 0.0
	

	@staticmethod
	def get_usdt_value(tickers: dict, asset: str, amount: float) -> float:

		if asset == 'USDT': 
			return amount
		
		if asset == 'NFT' or asset == '1000PEPPER':
			return 0.0
		
		try:
			ticker = tickers.get(f"{asset}USDT")
			price_in_usdt = float(ticker['price'])  

			return price_in_usdt * amount
		
		except Exception as e:
			print(f"No se pudo obtener el precio de {asset} en USDT. Exception: {e}")
			return 0.0
		
	
	@staticmethod
	def dateprint() -> str: 
		return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")  # format: 12/10/2024 20:30:234
	
	@staticmethod
	def dateprint_simple() -> str: 
		return datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # format: 12/10/2024 20:30:23
	

	@staticmethod
	def format_signal_message(event: SignalEvent) -> str:

		market = ""
		objet_price = ""

		if event.rsi is not None:
			if event.rsi > 70:
				market = "(mercado sobrecomprado)"
			elif event.rsi < 30:
				market = "(mercado sobrevendido)"
			else:
				market = "(mercado neutral)"

		title = f"\n📣 Señal de trading detectada 👀"
		action = 'compra' if event.signal.value == 'BUY' else 'venta'
		objet_price = 'entrada' if event.signal.value == 'BUY' else 'salida'

		message = (
			f"\n<b>Atención:</b> Se ha detectado una posible señal de <b>{action.upper()}</b> para <b>{event.symbol}</b>.\n\n"
			f"• Temporalidad de {event.timeframe}\n"
			f"• Estrategia aplicada: Cruce de Medias Móviles (MA) + RSI\n"
			f"• 🎯 Precio de {objet_price}: <b>{event.target_price:.2f} USD</b>\n"
		)

		if event.rsi is not None:
			rsi_value = round(event.rsi, 2)
			rsi_emoji = "🔥" if rsi_value > 70 or rsi_value < 30 else "💥"
			message += f"• {rsi_emoji} RSI: <b>{rsi_value}</b> {market}\n"

		message += f"• 🕒 Hora de generación: {Utils.dateprint_simple()}\n"
		message += "\n⚠️ No es una recomendación de inversión, solo un análisis técnico.\n"

		return title, message
