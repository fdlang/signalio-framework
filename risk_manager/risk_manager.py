from .interfaces.risk_manager_interface import IRiskManager
from .properties.risk_manager_properties import BaseRiskProps, MaxLeverageFactorRiskProps
from .risk_managers.max_leverage_factor_risk_manager import MaxLeverageFactorRiskManager
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from events.events import SizingEvent, OrderEvent

from queue import Queue


class RiskManager(IRiskManager):

    def __init__(self, events_queue: Queue, data_provider: DataProvider, portfolio: Portfolio, risk_properties: BaseRiskProps):
        self.events_queue = events_queue
        self.DATA_PROVIDER = data_provider
        self.PORTFOLIO = portfolio
        self.risk_management_method = self._get_risk_manament_method(risk_properties)


    def _get_risk_manament_method(self, risk_props: BaseRiskProps) -> IRiskManager:

        if isinstance(risk_props, MaxLeverageFactorRiskProps):
            return MaxLeverageFactorRiskManager(risk_props)
        else:
            raise Exception(f"ERROR: Método de Risk Manament desconocido: {risk_props}")
        

    def _create_and_put_order_event(self, sizing_event: SizingEvent, volume: float) -> None:

        # Crea el order_event a partir del sizing_event y el volumen
        order_event = OrderEvent(symbol=sizing_event.symbol,
                                    target_order=sizing_event.target_order,
                                    target_price=sizing_event.target_price,
                                    order_id=sizing_event.order_id,
                                    sl=sizing_event.sl,
                                    tp=sizing_event.tp,
                                    volume=sizing_event.volume)
        
        # Coloca el order_event en la cola de eventos
        self.events_queue.put(order_event)

    
    def assess_order(self, sizing_event: SizingEvent) -> None:
        
        # Obtiene el nuevo volumen  de la operacio que se quiere ejecutar después de pasar por el risk manager.
        new_volume = self.risk_management_method.assess_order(sizing_event, current_position_value, new_position_value)

        # Evalua el nuevo volumen
        if new_volume > 0.0:
            # coloca oder_event a la cola de eventos
            self._create_and_put_order_event(sizing_event, new_volume)

