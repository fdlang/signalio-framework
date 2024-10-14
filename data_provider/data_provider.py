import pandas as pd
from binance.exceptions import BinanceAPIException, BinanceRequestException
from typing import Dict
from datetime import datetime
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
            # Recupera los datos de las 2 ultimas velas
            klines = self.client.get_klines(symbol=symbol,interval=interval,limit=limit)

            if klines is None:
                print(f"El símbolo {klines} no existe o no se ha podido recuperar sus datos")

            else:
                # Crea la cabecera del DataFrame
                barss = pd.DataFrame(klines, columns=[
                    'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                    'Close time', 'Quote asset volume', 'Number of trades',
                    'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
                ])

                # Convierte la columna Open time a datatime
                barss['Open time'] = pd.to_datetime(barss['Open time'], unit='ms') 
                barss.set_index('Open time', inplace=True)

                # Renombra ciertas columnas
                barss.rename(columns={
                    'Quote asset volume':'Qte Asset Vol', 
                    'Number of trades':'Num Trades', 
                    'Taker buy base asset volume':'Taker Buy Vol', 
                    'Taker buy quote asset volume':'Taker Qte Vol'
                }, inplace=True) 

                # accede a la primera fila del dataframe 'penultima vela' 
                bars_np_array = barss.iloc[[0]] 

        except BinanceAPIException as e:
            print(f"El símbolo {symbol} no existe o no se ha podido recuperar sus datos.")
        except AttributeError as e:
            print(f"El intervalo de tiempo {interval} no es valido. Error: {e}")
        
        else:
            # si todo ok devuelve una serie
            return bars_np_array.iloc[-1]


    def get_latest_closed_bars(self, symbol: str, timeframe: str, num_bars: int = 1) -> pd.DataFrame:

        # Define los paramertros adecuados
        interval = timeframe # intervalo de tiempo para las velas 
        limit = num_bars if num_bars > 0 else 1
        
        try:
            # Recupera los datos de las 2 ultimas velas
            klines = self.client.get_klines(symbol=symbol,interval=interval,limit=limit)

            if klines is None:
                print(f"El símbolo {klines} no existe o no se ha podido recuperar sus datos")
                return pd.DataFrame()

            else:
                # Crea la cabecera del DataFrame
                barss = pd.DataFrame(klines, columns=[
                    'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
                    'Close time', 'Quote asset volume', 'Number of trades',
                    'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
                ])

                # Convierte la columna Open time a datatime
                barss['Open time'] = pd.to_datetime(barss['Open time'], unit='ms') 
                barss.set_index('Open time', inplace=True)

                # Renombra ciertas columnas
                barss.rename(columns={
                    'Quote asset volume':'Qte Asset Vol', 
                    'Number of trades':'Num Trades', 
                    'Taker buy base asset volume':'Taker Buy Vol', 
                    'Taker buy quote asset volume':'Taker Qte Vol'
                }, inplace=True) 

        except BinanceAPIException as e:
            print(f"No se han podido recuperar los datos de la última vela de {symbol} {timeframe}. ERROR: {e} ")
        except AttributeError as e:
            print(f"El intervalo de tiempo {interval} no es valido.")
        
        else:
            # si todo ok devuelve el dataframe
            return barss


    def get_latest_tick(self, symbol: str) -> dict:

        try:
            tick = self.client.get_recent_trades(symbol=symbol, limit=1)

            if tick is None:
                print(f"No se ha podido recuperar el últinmo tick de {symbol}")
                return None

        except BinanceAPIException as e:
            print(f"No se ha podido recuperar el ultimo tick, el símbolo {symbol} no es correcto")
            return None
        except BinanceRequestException as e:
            print(f"Algo no ha salido bien a la hora de recuperar el último tick. Binance Error: {e}")
            return None
        except Exception as e:
            print(f"Algo no ha salido bien a la hora de recuperar el último tick. Error: {e}")
            return None
        
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
    
    def get_usdt_value(self, asset, amount):

        if asset == 'USDT':  # Si la moneda es USDT, no hace falta convertir
            return float(amount)
        try:
            # Obtiene el precio de la moneda en USDT
            ticker = self.client.get_symbol_ticker(symbol=f"{asset}USDT")
            price_in_usdt = float(ticker['price'])
            return price_in_usdt * float(amount)
        except Exception as e:
            # Si no existe un par directo en USDT, se ignora
            print(f"No se pudo obtener el precio de {asset} en USDT: {e}")
            return 0
        

    def get_account_balance_usdt(self):
        # Calcula el saldo total de la billetera en USDT
        total_usdt_value = 0

        for balance in self.client.account_info['balances']:
            asset = balance['asset']
            free_balance = balance['free']

            if float(free_balance) > 0:
                total_usdt_value += self.get_usdt_value(asset, free_balance)

        return total_usdt_value


                

    