from platform_connector.plaform_connector import PlatformConnector
from data_provider.data_provider import DataProvider
from trading_director.trading_director import TradingDirector
from signal_generator.signals.signal_ma_crossover import SignalMACrossover
from position_sizer.position_sizer import PositionSizer
from position_sizer.properties.position_sizer_properties import MinSizingProps, FixedSizingProps, RiskPctSizingProps
from queue import Queue


if __name__ == "__main__":

    try:
        symbols = ['ADABTC','ETHBTC', 'SOLUSDT']
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
        POSITION_SIZER = PositionSizer(events_queu=events_queue,
                                        data_provider=DATA, 
                                        sizing_properties=FixedSizingProps(volume=0.09))

        # Crea el trading director y ejecuta el metodo principal
        TRADING_DIRECTOR = TradingDirector(events_queue=events_queue, data=DATA, signal_generator=SIGNAL_GENERATOR, position_sizer=POSITION_SIZER)
        TRADING_DIRECTOR.execute()

    except KeyboardInterrupt:
        print(f"\nEjecución interrumpida por el usuario.")
        exit() 


   