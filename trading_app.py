from platform_connector.plaform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from queue import Queue


if __name__ == "__main__":

    symbols = ['ADABTC','ETHBTC']
    timeframe = "1m"
    slow_ma_perid = 50
    fast_ma_perid = 14

    # creación de la cola de eventos principal
    events_queue = Queue()

    # creación modulos principales del framework
    CONNECT = PlatformConnector(symbols=symbols)
    DATA = DataProvider(CONNECT.client, 
                        events_queue=events_queue, 
                        symbol_list=symbols, 
                        timeframe=timeframe)
    SIGNAL_GENERATOR = SignalMACrossover(event_queue=events_queue, 
                                        data=DATA, 
                                        timeframe=timeframe, 
                                        fast_period=fast_ma_perid, 
                                        slow_period=slow_ma_perid)

    # Crea el trading director y ejecuta el metodo principal
    TRADING_DIRECTOR = TradingDirector(events_queue=events_queue, data=DATA, signal_generator=SIGNAL_GENERATOR)
    TRADING_DIRECTOR.execute()
   