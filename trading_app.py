from platform_connector.plaform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from position_sizer.position_sizer import PositionSizer
from position_sizer.properties.position_sizer_properties import MinSizingProps, FixedSizingProps, RiskPctSizingProps
from portfolio.portfolio import Portfolio
from risk_manager.risk_manager import RiskManager
from risk_manager.properties.risk_manager_properties import MaxLeverageFactorRiskProps
from order_executor.spot_order_executor import SpotOrderExecutor
from notifications.notification import NotificationService, TelegramNotificationProperties

from queue import Queue
import os


if __name__ == "__main__":

    try:
        symbols = ['HBARUSDT', 'SOLUSDT']
        timeframe = "4h"
        new_order_id = 12345
        slow_ma_perid = 50
        fast_ma_perid = 14

        # creación de la cola de eventos principal
        events_queue = Queue()

        # creación modulos principales del framework
        CONNECT = PlatformConnector(symbols=symbols)
        
        DATA_PROVIDER = DataProvider(CONNECT.client, 
                            events_queue=events_queue, 
                            symbol_list=symbols, 
                            timeframe=timeframe)
        
        PORTFOLIO = Portfolio(order_id= new_order_id, 
                              data_provider=DATA_PROVIDER)
        
        POSITION_SIZER = PositionSizer(events_queu=events_queue,
                                        data_provider=DATA_PROVIDER, 
                                        sizing_properties=FixedSizingProps(volume=1.00))    # % de riesgo
        

        RISK_MANAGER = RiskManager(events_queue=events_queue,
                                   data_provider=DATA_PROVIDER,
                                   portfolio=PORTFOLIO,
                                   risk_properties=MaxLeverageFactorRiskProps(max_leverage_factor=2))
        
        ORDER_EXECUTOR = SpotOrderExecutor(connector=CONNECT,
                                           events_queue=events_queue,
                                           portfolio=PORTFOLIO,
                                           )
        
        SIGNAL_GENERATOR = SignalMACrossover(event_queue=events_queue, 
                                            data=DATA_PROVIDER, 
                                            portfolio=PORTFOLIO,
                                            spot_order_executer=ORDER_EXECUTOR,
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
                                           position_sizer=POSITION_SIZER,
                                           risk_manager=RISK_MANAGER,
                                           order_execute=ORDER_EXECUTOR,
                                           notification_service=NOTIFICATIONS)
        
        TRADING_DIRECTOR.execute()

    except KeyboardInterrupt:
        print(f"\nEjecución interrumpida por el usuario.")
        exit() 


   