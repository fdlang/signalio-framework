import pandas as pd
from binance.exceptions import BinanceAPIException, BinanceRequestException
from typing import Dict
from datetime import datetime, timezone
from events.events import DataEvent
from queue import Queue


class DataProvider():

	def __init__(self, client, events_queue: Queue, symbol_list: list, timeframe: str):
		self.client = client
		self.events_queue = events_queue  # recibe una cola de eventos
		self.symbols: list = symbol_list
		self.timeframe: str = timeframe

		# Diccionario para guardar el datetime de la última vela de cada símbolo
		self.last_bar_datetime:Dict[str, datetime] = {symbol:datetime.min for symbol in self.symbols} 


	def _map_timeframes(self,timeframe: str) -> int:

		# crea un diccionario para temporalidades
		timeframe_mapping = {
			'1m':self.client.KLINE_INTERVAL_1MINUTE,
			'3m':self.client.KLINE_INTERVAL_3MINUTE,
			'5m':self.client.KLINE_INTERVAL_5MINUTE,
			'15m':self.client.KLINE_INTERVAL_15MINUTE,
			'30m':self.client.KLINE_INTERVAL_30MINUTE,
			'1h':self.client.KLINE_INTERVAL_1HOUR,
			'2h':self.client.KLINE_INTERVAL_2HOUR,
			'4h':self.client.KLINE_INTERVAL_4HOUR,
			'6h':self.client.KLINE_INTERVAL_6HOUR,
			'8h':self.client.KLINE_INTERVAL_8HOUR,
			'12h':self.client.KLINE_INTERVAL_12HOUR,
			'1d':self.client.KLINE_INTERVAL_1DAY,
			'1w':self.client.KLINE_INTERVAL_1WEEK,
			'1M':self.client.KLINE_INTERVAL_1MONTH
		} 

		try:
			return timeframe_mapping[timeframe]
		except:
			print(f"TimeFrame {timeframe} no valido!")


	def get_latest_closed_bar(self, symbol: str, timeframe: str) -> pd.Series:

		# Define los paramertros adecuados
		interval = self._map_timeframes(timeframe) # intervalo de tiempo para las velas 
		limit = 2 # limite de velas

		try:
			# Recupera los datos de las ultimas velas
			klines = self.client.get_klines(symbol=symbol,interval=interval,limit=limit)

			if klines is None:
				print(f"El símbolo {klines} no existe o no se ha podido recuperar sus datos")
				return pd.Series()

			else:
				# Crea la cabecera del DataFrame
				barss = pd.DataFrame(klines, columns=[
					'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
					'Close time', 'Quote asset volume', 'Number of trades',
					'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
				])

				# Convierte la columna Open time a datatime
				barss['Open time'] = pd.to_datetime(barss['Open time'], unit='ms') 
				barss['Close time'] = pd.to_datetime(barss['Close time'], unit='ms') 

				barss['Close time'] = barss['Close time'].dt.tz_localize('UTC')
				
				barss.set_index('Open time', inplace=True)

				# Renombra ciertas columnas
				barss.rename(columns={
					'Quote asset volume':'Qte Asset Vol', 
					'Number of trades':'Num Trades', 
					'Taker buy base asset volume':'Taker Buy Vol', 
					'Taker buy quote asset volume':'Taker Qte Vol'
				}, inplace=True) 

				closed_candles = barss[barss['Close time'] <= datetime.now(timezone.utc)]

				if not closed_candles.empty:
					latest_closed_candle = closed_candles.iloc[-1]
					
					return latest_closed_candle # Si hay velas cerradas, devuelve la última vela cerrada

				else:
					print("No hay velas cerradas en el tiempo especificado.")
					return pd.Series()

		except BinanceAPIException as e:
			print(f"El símbolo {symbol} no existe o no se ha podido recuperar sus datos.")
		except AttributeError as e:
			print(f"El intervalo de tiempo {interval} no es valido. Error: {e}")
		except BinanceRequestException as e:
			print(f'Error de solicitud a Binance: {e}')

		# si algo sale mal devuelve series vacias
		return pd.Series()


	def get_latest_closed_bars(self, symbol: str, timeframe: str, num_bars: int = 1) -> pd.DataFrame:

		# Define los paramertros adecuados
		interval = self._map_timeframes(timeframe) # intervalo de tiempo para las velas 
		limit = num_bars if num_bars > 0 else 1
		
		try:
			# Recupera los datos de las ultimas velas
			klines = self.client.get_klines(symbol=symbol,interval=interval,limit=limit)

			if klines is None:
				print(f"El símbolo {klines} no existe o no se ha podido recuperar sus datos")
				return pd.DataFrame()

			
			# Crea la cabecera del DataFrame
			barss = pd.DataFrame(klines, columns=[
				'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
				'Close time', 'Quote asset volume', 'Number of trades',
				'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
			])

			# Convierte la columna Open time a datatime
			barss['Open time'] = pd.to_datetime(barss['Open time'], unit='ms') 
			barss['Close time'] = pd.to_datetime(barss['Close time'], unit='ms').dt.tz_localize('UTC')

			barss.set_index('Open time', inplace=True)

			# Renombra ciertas columnas
			barss.rename(columns={
				'Quote asset volume':'Qte Asset Vol', 
				'Number of trades':'Num Trades', 
				'Taker buy base asset volume':'Taker Buy Vol', 
				'Taker buy quote asset volume':'Taker Qte Vol'
			}, inplace=True) 
				
			# Filtrar solo las velas que ya han cerrado
			now_utc = datetime.now(timezone.utc)
			closed_candles = barss[barss['Close time'] <= now_utc]

			# Devolver solo las últimas `num_bars` velas cerradas
			return closed_candles.tail(num_bars)

		except BinanceAPIException as e:
			print(f"No se han podido recuperar los datos de la última vela de {symbol} {timeframe}. ERROR: {e} ")
		except AttributeError as e:
			print(f"El intervalo de tiempo {interval} no es valido.")
		except BinanceRequestException as e:
			print(f'Error de solicitud a Binance: {e}')
		
		# si algo sale mal devuelve el dataframe vacio
		return pd.DataFrame()


	def get_latest_tick(self, symbol: str) -> dict:

		try:
			tick = self.client.get_ticker(symbol=symbol)

			if tick is None:
				print(f"El símbolo {symbol} no existe o no se ha podido recuperar sus datos.")
				return {}

		except BinanceAPIException as e:
			print(f"No se ha podido recuperar el ultimo tick, el símbolo {symbol} no es correcto - Binance Error: {e}")
			return {}
		except BinanceRequestException and AttributeError as e:
			print(f"Algo no ha salido bien a la hora de recuperar el último tick - Binance Error: {e}")
			return {}
		
		else:
			return tick
	

	def get_bid_ask(self, symbol: str) -> dict:

		try:
			order_book = self.client.get_order_book(symbol=symbol)
			bid = order_book['bids'][0][0] if order_book['bids'] else None
			ask = order_book['asks'][0][0] if order_book['asks'] else None

			return {"bid": bid, "ask": ask}
		except Exception as e:
			print(f"Error al obtener bid y ask: {e}")
			return None


	def check_for_new_data(self) -> None:

		# Compruba si hay datos nuevos
		for symbol in self.symbols:
			last_bar = self.get_latest_closed_bar(symbol, self.timeframe)

			if last_bar is None:
				continue
			
			# si hay datos nuevos
			if not last_bar.empty and last_bar.name > self.last_bar_datetime[symbol]:
				# Actualiza la última vela recuperada
				self.last_bar_datetime[symbol] = last_bar.name

				# crera DataEvent y se añade a la cola de eventos
				data_event = DataEvent(symbol=symbol, data=last_bar)

				# se añade a la cola de eventos
				self.events_queue.put(data_event)


	def get_account_usdt(self):
		account_info = self.client.get_account()
		usdt_account = 0.0

		for balance in account_info['balances']:
			if balance['asset'] == 'USDT':
				usdt_account = float(balance['free'])
				
		return usdt_account


				

	