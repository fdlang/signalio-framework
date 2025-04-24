from data_provider.data_provider import DataProvider
from signal_generator.interfaces.signal_generator_interface import ISignalGererator
from events.events import DataEvent, SignalEvent
from notifications.notification import NotificationService

from typing import Dict, Callable
from utils.utils import Utils
import queue, time


class TradingDirector():

    def __init__(self, events_queue: queue.Queue, data: DataProvider, signal_generator: ISignalGererator, 
                 notification_service: NotificationService):

        self.events_queue = events_queue

        # referencia de los distintos módulos
        self.DATA = data
        self.SIGNAL_GENERATOR = signal_generator
        self.NOTIFICATIONS = notification_service

        # controlador de trading
        self.continue_trading: bool = True

        # crea el evento handler
        self.event_handler:Dict[str, Callable] = {
            "DATA": self._handle_data_event, 
            "SIGNAL": self._handle_signal_event,
        }



    def _handle_signal_event(self, event: SignalEvent):
        print(f"{Utils.dateprint()} - Recibido SIGNAL EVENT de {event.signal} para {event.symbol}")
        self._process_execution_or_pending_events(event)


    def _handle_data_event(self, event:DataEvent):
        print(f"{Utils.dateprint()} - Recibido DATA EVENT de {event.symbol} - Último precio de cierre {event.data.Close}")
        self.SIGNAL_GENERATOR.generate_signal(event)

    
    def _process_execution_or_pending_events(self, event: SignalEvent | DataEvent) -> None:
        # aquí se puede colocar codigo para generar mensajes de telegram o lo que se necesite. 
        
        if isinstance(event, SignalEvent):
            self.NOTIFICATIONS.send_notification(tittle=f"Señal de trading", 
                                                 message=f"Posible señal de {event.signal.value} para {event.symbol} - Precio objetivo: {event.target_price} $ - ID de orden: {event.order_id}")  
        

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