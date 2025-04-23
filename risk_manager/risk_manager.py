from .interfaces.risk_manager_interface import IRiskManager
from .properties.risk_manager_properties import BaseRiskProps, MaxLeverageFactorRiskProps
from .risk_managers.max_leverage_factor_risk_manager import MaxLeverageFactorRiskManager
from data_provider.data_provider import DataProvider
from portfolio.portfolio import Portfolio
from events.events import SizingEvent, OrderEvent
from binance.client import Client
from utils.utils import Utils

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
        

    def _compute_current_value_of_positions_in_account_currency(self) -> float:

        # Recopila las posiciones abiertas
        current_position = self.PORTFOLIO.get_strategy_open_position()

        # Calcula el valor de las posiciones abiertas
        total_value = 0.0

        for position in current_position:
            total_value += self._compute_value_of_position_in_account_currency()

        return total_value
    

    def _compute_value_of_position_in_account_currency(self, symbol: str, volume: float, position_type: str) -> float:

        symbol_info = Client().get_symbol_info(symbol)
        min_qty = float(symbol_info['filters'][1]['minQty'])
        traded_units =  0.0                                     # Unidades operadas en las unidades del symbol

        if volume >= min_qty:
            traded_units = volume

            # Valor de las unidades operadas en la divisa cotizada del simbolo
            value_traded_in_profit_ccy = traded_units * float(self.DATA_PROVIDER.get_latest_tick(symbol)["bidPrice"])

            # Valor de las unidades operadas en la divisa de la cuenta
            value_traded_in_account_ccy = Utils.convert_currency_amount_to_another_currency(value_traded_in_profit_ccy, 
                                                                                            symbol_info['quoteAsset'], 
                                                                                            "USDT")
            if position_type == Client().SIDE_SELL:
                return -value_traded_in_account_ccy
            else:
                return value_traded_in_account_ccy
        else:
            print(f"ERROR (RiskManager): El volumen {volume} es inferior a las unidades permitidas {min_qty}")
        

    def _create_and_put_order_event(self, sizing_event: SizingEvent, volume: float) -> None:

        # Crea el order_event a partir del sizing_event y el volumen
        order_event = OrderEvent(symbol=sizing_event.symbol,
                                    signal=sizing_event.signal,
                                    target_order=sizing_event.target_order,
                                    target_price=sizing_event.target_price,
                                    order_id=sizing_event.order_id,
                                    sl=sizing_event.sl,
                                    tp=sizing_event.tp,
                                    volume=volume)
        
        # Coloca el order_event en la cola de eventos
        self.events_queue.put(order_event)

    
    def assess_order(self, sizing_event: SizingEvent) -> None:

        # Obtiene el valor de todas las posiciones abiertas por la estrategia en la divisa de la cuenta.
        current_position_value = self._compute_current_value_of_positions_in_account_currency()

        # Obtiene el valor que tiene la nueva posición en la divisa de la cuenta
        position_type = Client().SIDE_BUY if sizing_event.signal == "BUY" else Client().SIDE_SELL
        new_position_value = self._compute_value_of_position_in_account_currency(sizing_event.symbol, sizing_event.volume, position_type)
        
        # Obtiene el nuevo volumen  de la operacio que se quiere ejecutar después de pasar por el risk manager.
        new_volume = self.risk_management_method.assess_order(self.DATA_PROVIDER, sizing_event, current_position_value, new_position_value)

        # Evalua el nuevo volumen
        if new_volume > 0.0:
            # coloca oder_event a la cola de eventos
            self._create_and_put_order_event(sizing_event, new_volume)

