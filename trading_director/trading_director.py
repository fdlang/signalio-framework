from data_provider.data_provider import DataProvider
from events.events import DataEvent
from typing import Dict, Callable
from datetime import datetime
import queue, time



class TradingDirector():

    def __init__(self, events_queue: queue.Queue, data: DataProvider):

        self.events_queue = events_queue

        # referencia de los distintos módulos
        self.DATA = data

        # controlador de trading
        self.continue_trading: bool = True

        # crea el evento handler
        self.event_handler:Dict[str, Callable] = {
            "DATA":self._handle_data_event, 
        }


    def _dateprint(self) -> str: 
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f") # format: 12/10/2024 20:30:234


    def _handle_data_event(self, event:DataEvent):
        # Gestiona los eventos de tipo DataEvent
        print(f"{event.data.name} - Recibidos nuevos datos de {event.symbol} - Último precio de cierre {event.data.Close}")

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
            
            time.sleep(1)
        
        print("FIN")