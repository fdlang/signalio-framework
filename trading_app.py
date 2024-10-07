from platform_connector.plaform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from queue import Queue


if __name__ == "__main__":

    symbols = ['ADABTC','ETHBTC','SOLBTC','BTCUSDT','INJBTC','FETBTC']
    timeframe = "1min"

    # creación de la cola de eventos principal
    events_queue = Queue()

    # creación modulos principales del framework
    CONNECT = PlatformConnector(symbols)
    DATA = DataProvider(CONNECT.client, events_queue=events_queue, symbol_list=symbols, timeframe=timeframe)

    # Crea el trading director y ejecuta el metodo principal
    TRADING_DIRECTOR = TradingDirector(events_queue=events_queue, data=DATA)
    TRADING_DIRECTOR.execute()
   