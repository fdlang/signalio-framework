import pandas as pd


class DataProvider():

    def __init__(self, client):
        self.client = client


    def _map_timeframes(self,timeframe:str) -> int:

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


    def get_latest_closed_bar(self, symbol:str, timeframe:str):

        # Define los paramertros adecuados
        interval = self.client.KLINE_INTERVAL_1HOUR # intervalo de tiempo para las velas 
        limit = 2 # limite de velas

        # Recupera los datos de las 2 ultimas velas
        klines = self.client.get_klines(symbol=symbol,interval=interval,limit=limit)

        # Crea la cabecera del DataFrame
        barss = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])

        # formatea la fecha
        barss['Open time'] = pd.to_datetime(barss['Open time'], unit='ms') 

        # accede a la primera fila del dataframe 'penultima vela' 
        bars = barss.iloc[[0]] 
        bars