import pandas as pd
from binance.exceptions import BinanceAPIException, BinanceRequestException


class DataProvider():

    def __init__(self, client):
        self.client = client


    def _map_timeframes(self,timeframe:str) -> str:

        # crea un diccionario para temporalidades
        timeframe_mapping = {
            '1min':self.client.KLINE_INTERVAL_1MINUTE,
            '3min':self.client.KLINE_INTERVAL_3MINUTE,
            '5min':self.client.KLINE_INTERVAL_5MINUTE,
            '15min':self.client.KLINE_INTERVAL_15MINUTE,
            '30min':self.client.KLINE_INTERVAL_30MINUTE,
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


    def get_latest_closed_bar(self, symbol:str, timeframe:str) -> pd.Series:

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


    def get_latest_closed_bars(self, symbol:str, timeframe:str, num_bars:int = 1) -> pd.DataFrame:

        # Define los paramertros adecuados
        interval = timeframe # intervalo de tiempo para las velas 
        limit = num_bars if num_bars > 0 else 1
        
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

        except BinanceAPIException as e:
            print(f"El símbolo {symbol} no existe o no se ha podido recuperar sus datos.")
        except AttributeError as e:
            print(f"El intervalo de tiempo {interval} no es valido.")
        
        else:
            # si todo ok devuelve el dataframe
            return barss


    def get_latest_tick(self, symbol:str) -> dict:

        try:
            tick = self.client.get_recent_trades(symbol=symbol,limit=1)

            if tick is None:
                print(f"No se ha podido recuperar el últinmo tick de {symbol}")

        except BinanceAPIException as e:
            print(f"No se ha podido recuperar el ultimo tick, el símbolo {symbol} no es correcto")
        except BinanceRequestException as e:
            print(f"Algo no ha salido bien a la hora de recuperar el último tick. Binance Error: {e}")
        except Exception as e:
            print(f"Algo no ha salido bien a la hora de recuperar el último tick. Error: {e}")
        
        else:
            return tick