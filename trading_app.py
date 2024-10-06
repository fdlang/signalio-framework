from platform_connector.plaform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from queue import Queue

if __name__ == "__main__":

    symbols = ['ADAUSDT','ETHBTC','ETHHBTC']
    timeframe = "1min"

    # creación de la cola de eventos principal
    events_queue = Queue()

    # creación modulos principales del framework
    CONNECT = PlatformConnector(symbols)
    DATA = DataProvider(CONNECT.client, events_queue=events_queue, symbol_list=symbols, tiemframe=timeframe)
    

   