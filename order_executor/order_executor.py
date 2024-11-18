from queue import Queue
from portfolio.portfolio import Portfolio
from events.events import OrderEvent
from platform_connector.plaform_connector import PlatformConnector


class OrderExecutor():

    def __init__(self, events_queue: Queue, portfolio: Portfolio, client: PlatformConnector):

        self.events_queue = events_queue
        self.PORTFOLIO = portfolio
        self.client = client.client


    def excute_order(self, order_event: OrderEvent) -> None:

        # Evalua el tipo de orden que se quiere ejecutar y llama al método
        if order_event.target_order == "MARKET":
            pass
        else:
            pass

    
    def _execute_market_order(self, order_event: OrderEvent) -> None:

       # comprueba si la orden es de venta o compra
       if order_event.signal == "BUY" :
           order_side = self.client.SIDE_BUY
       elif order_event.signal == "SELL":
           order_side = self.client.SIDE_SELL
       else:
           raise Exception(f"ORDER EXECUTOR: La señal {order_event.signal} no es válida.")
       
       market_order = self.client.create_order(
           
           symbol=order_event.symbol,
           side=order_side,
           type=self.client.ORDER_TYPE_MARKET,
           quantity=order_event.volume
       )

       