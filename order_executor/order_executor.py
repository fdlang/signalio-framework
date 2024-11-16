from queue import Queue
from portfolio.portfolio import Portfolio
from events.events import OrderEvent


class OrderExecutor():

    def __init__(self, events_queue: Queue, portfolio: Portfolio):

        self.events_queue = events_queue
        self.PORTFOLIO = portfolio


    def excute_order(self, order_event: OrderEvent) -> None:

        # Evalua el tipo de orden que se quiere ejecutar y llama al método
        if order_event.target_order == "MARKET":
            pass
        else:
            pass
