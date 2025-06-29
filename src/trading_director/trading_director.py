from src.data_provider.data_provider import DataProvider
from src.signal_generator.interfaces.signal_generator_interface import ISignalGenerator
from src.events.events import DataEvent, SignalEvent
from src.notifications.notification import NotificationService

from typing import Dict, Callable
from src.utils.utils import Utils 
import queue, time


class TradingDirector():

    def __init__(self, events_queue: queue.Queue, data: DataProvider, signal_generator: ISignalGenerator, 
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

            tittle, message = Utils.format_signal_message(event)
            self.NOTIFICATIONS.send_notification(tittle=tittle, message=message)
        

    def _handle_none_event(self, event):
        print(f"{Utils.dateprint()} - ERROR: Recibido evento nulo. Terminando ejecución del Framework")
        self.continue_trading = False


    def _handle_unknown_event(self, event):
        print(f"{Utils.dateprint()} - ERROR: Evento desconocido. Terminando ejecución del Framework. - Evento: {event}")
        self.continue_trading = False


    def execute(self) -> None:
        """
        Método principal del director de trading. Se encarga de recibir los eventos y procesarlos.
        """
        while self.continue_trading:
            try:
                event = self.events_queue.get(block=False) # Cola FIFO (el primer evento que entra es el primero en salir)
            except queue.Empty:
                self.DATA.check_for_new_data() 

            else:
                if event is not None:
                    handler = self.event_handler.get(event.event_type, self._handle_unknown_event)
                    handler(event)
                else:
                    self._handle_none_event(event)
                    
            time.sleep(0.02) # Tiempo de carga para evitar el uso excesivo de CPU (0.2 = 5 veces por segundo)
        
        print("FIN")