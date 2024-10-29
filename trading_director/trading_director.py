from data_provider.data_provider import DataProvider
from signal_generator.interfaces.signal_generator_interface import ISignalGererator
from position_sizer.position_sizer import PositionSizer
from risk_manager.risk_manager import RiskManager
from events.events import DataEvent, SignalEvent, SizingEvent, OrderEvent
from typing import Dict, Callable
from datetime import datetime
import queue, time


class TradingDirector():

    def __init__(self, events_queue: queue.Queue, data: DataProvider, signal_generator: ISignalGererator, position_sizer: PositionSizer, risk_manager: RiskManager):

        self.events_queue = events_queue

        # referencia de los distintos módulos
        self.DATA = data
        self.SIGNAL_GENERATOR = signal_generator
        self.POSITION_SIZER = position_sizer
        self.RISK_MANAGER = risk_manager

        # controlador de trading
        self.continue_trading: bool = True

        # crea el evento handler
        self.event_handler:Dict[str, Callable] = {
            "DATA": self._handle_data_event, 
            "SIGNAL": self._handle_signal_event,
            "SIZING": self._handle_sizing_event,
            "ORDER": self._handle_order_event,
        }


    def _dateprint(self) -> str: 
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f") # format: 12/10/2024 20:30:234


    def _handle_signal_event(self, event= SignalEvent):
        # Procesa el signal event
        print(f"{self._dateprint()} - Recibido SIGNAL EVENT de {event.signal} para {event.symbol}")
        self.POSITION_SIZER.size_signal(event)


    def _handle_data_event(self, event:DataEvent):
        # Gestiona los eventos de tipo DataEvent
        print(f"{self._dateprint()} - Recibido DATA EVENT de {event.symbol} - Último precio de cierre {event.data.Close}")
        self.SIGNAL_GENERATOR.generate_signal(event)
    

    def _handle_sizing_event(self, event: SizingEvent):
        print(f"{self._dateprint()} - Recibido SIZING EVENT con volumen {event.volume}  para {event.signal} en {event.symbol}")
        self.RISK_MANAGER.assess_order(event)

    
    def _handle_order_event(self, event: OrderEvent):
        print(f"{self._dateprint()} - Recibido ORDER EVENT con volumen {event.volume}  para {event.signal} en {event.symbol}")


    def execute(self) -> None:

        while self.continue_trading:
            try:
                event = self.events_queue.get(block=False) # Cola FIFO (el primer evento que entra es el primero en salir)
            except queue.Empty:
                self.DATA.check_for_new_data() 

            else:
                if event is not None:
                    handler = self.event_handler.get(event.event_type)
                    handler(event)
                else:
                    self.continue_trading = False
                    print(f"ERROR: Recibido evento nulo. Terminando ejecución del Framework")
            
            time.sleep(0.01)
        
        print("FIN")