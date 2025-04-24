
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from platform_connector.plaform_connector import PlatformConnector
from notifications.notification import NotificationService, TelegramNotificationProperties

from queue import Queue
import os


if __name__ == "__main__":

    try:
        symbols = ['BTCUSDC', 'SOLUSDC']
        timeframe = "4h"
        new_order_id = 12345
        slow_ma_perid = 50
        fast_ma_perid = 14

        # creación de la cola de eventos principal
        events_queue = Queue()

        # creación modulos principales del framework
        CONNECT = PlatformConnector(symbols=symbols)
        
        DATA_PROVIDER = DataProvider(CONNECT, 
                            events_queue=events_queue, 
                            symbol_list=symbols, 
                            timeframe=timeframe)
        
        
        SIGNAL_GENERATOR = SignalMACrossover(event_queue=events_queue, 
                                            data=DATA_PROVIDER, 
                                            timeframe=timeframe, 
                                            fast_period=fast_ma_perid, 
                                            slow_period=slow_ma_perid)
        
        NOTIFICATIONS = NotificationService(
            properties=TelegramNotificationProperties(token=os.getenv('token'),
                                                      chat_id=os.getenv('chat_id')))
        
        
        # Crea el trading director y ejecuta el metodo principal
        TRADING_DIRECTOR = TradingDirector(events_queue=events_queue, 
                                           data=DATA_PROVIDER, 
                                           signal_generator=SIGNAL_GENERATOR, 
                                           notification_service=NOTIFICATIONS)
        
        TRADING_DIRECTOR.execute()

    except KeyboardInterrupt:
        print(f"\nEjecución interrumpida por el usuario.")
        exit() 


   