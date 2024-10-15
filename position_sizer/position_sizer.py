from data_provider.data_provider import DataProvider
from events.events import SignalEvent, SizingEvent
from binance.client import Client
from .interfaces.position_sizer_interface import IPositionSizer
from .properties.position_sizer_properties import BaseSizerProps, MinSizingProps, FixedSizingProps, RiskPctSizingProps
from .sizers.min_size_position_sizer import MinSizePositionSizer
from .sizers.fixed_size_position_sizer import FixedSizePositionSizer
from .sizers.risk_pct_position_sizer import RiskPctPositionSizer
from queue import Queue


class PositionSizer(IPositionSizer):

    def __init__(self, events_queu: Queue, data_provider: DataProvider, sizing_properties: BaseSizerProps):
        self.events_queue = events_queu
        self.DATA_PROVIDER = data_provider
        self.position_sizing_method = self._get_position_sizing_method(sizing_properties)

    
    def _get_position_sizing_method(self, sizing_props: BaseSizerProps ) -> IPositionSizer:
        """
        Devuelve una instancia del position sizer apropiado en función del objeto de propiedades recibido.
        """

        if isinstance(sizing_props, MinSizingProps):
            return MinSizePositionSizer()
        
        elif isinstance(sizing_props, FixedSizingProps):
            return FixedSizePositionSizer(properties=sizing_props)
        
        elif isinstance(sizing_props, RiskPctSizingProps):
            return RiskPctPositionSizer(properties=sizing_props)
        
        else:
            raise(f"ERROR: Método de sizing desconocido: {sizing_props}")


    def __create_and_put_sizing_event(self, signal_event: SignalEvent, volume: float) -> None:

        # Crea el sizing event a partir del signal event y el volumen
        sizing_event = SizingEvent(symbol=signal_event.symbol,
                                    signal=signal_event.signal,
                                    target_order=signal_event.target_order,
                                    target_price=signal_event.target_price,
                                    order_id=signal_event.order_id,
                                    sl=signal_event.sl,
                                    tp=signal_event.tp,
                                    volume=volume)
        
        # Colaca el sizing event a la cola de eventos
        self.events_queue.put(sizing_event)
        

    def size_signal(self, signal_event: SignalEvent) -> None:
        
        # Obtiene el volumen adecuado segun el metodo de sizzing
        volume = self.position_sizing_method.size_signal(signal_event, self.DATA_PROVIDER)

        # Control de seguridad
        if volume < Client().get_symbol_info(signal_event.symbol)['filters'][1]['minQty']:
            print(f"ERROR: El volumen {volume} es menor al volumen mínimo admitido por el símbolo {signal_event.symbol}")
            return None

        # Crea el evento y lo pone en la cola
        self.__create_and_put_sizing_event(signal_event, volume) 