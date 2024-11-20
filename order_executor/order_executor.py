from portfolio.portfolio import Portfolio
from events.events import OrderEvent, ExecutionEvent, SignalType
from platform_connector.plaform_connector import PlatformConnector
import pandas as pd

from queue import Queue


class OrderExecutor():

	def __init__(self, events_queue: Queue, portfolio: Portfolio, client: PlatformConnector):

		self.events_queue = events_queue
		self.PORTFOLIO = portfolio
		self.client = client.client


	def excute_order(self, order_event: OrderEvent) -> None:

		# Evalua el tipo de orden que se quiere ejecutar y llama al método
		if order_event.target_order == "MARKET":
			self._execute_market_order(order_event)
		else:
			self._send_pending_order(order_event)

	
	def _execute_market_order(self, order_event: OrderEvent) -> None:

		# comprueba si la orden es de venta o compra
		if order_event.signal == "BUY" :
			order_side = self.client.SIDE_BUY
		elif order_event.signal == "SELL":
			order_side = self.client.SIDE_SELL
		else:
			raise Exception(f"ORDER EXECUTOR: La señal {order_event.signal} no es válida.")
		
		market_order = self.client.create_order(symbol=order_event.symbol,
												side=order_side,
												type=self.client.ORDER_TYPE_MARKET,
												quantity=order_event.volume,
												newClientOrderId = order_event.order_id)

		# Verifica el resultado de la ejecución de la orden 
		if self._check_execute_status(market_order):
			print(f"Market Order {order_event.signal} para {order_event.symbol} de {order_event.volume} ejecutado correctamente.")
			self._create_put_execute_event(market_order)
		else:
			print(f"Ha habido un error al ejecutar la orden {order_event.signal} para {order_event.symbol}")
	

	def _check_execute_status(self, market_order) -> bool:

		if market_order['status'] == self.client.ORDER_STATUS_FILLED:
			return True
		elif market_order['status'] == self.client.ORDER_STATUS_PARTIALLY_FILLED:
			return True
		else:
			return False
	

	def _send_pending_order(self, order_event: OrderEvent) -> None:

		# comprueba si es de tipo STOP_LOSS o LIMIT
		if order_event.target_order == "STOP_LOSS_LIMIT":
			
			order_type = self.client.ORDER_TYPE_STOP_LOSS_LIMIT
			side_type = self.client.SIDE_BUY if order_event.signal == "BUY" else self.client.SIDE_SELL

		elif order_event.target_order == "LIMIT":

			order_type = self.client.ORDER_TYPE_LIMIT
			side_type = self.client.SIDE_BUY if order_event.signal == "BUY" else self.client.SIDE_SELL
		else:
			raise Exception(f"ORDER EXECUTE: La orden pendiente objetivo {order_event.target_order} no es válida.")

		pending_order = self.client.create_order(symbol =order_event.symbol,
												side = side_type,
												type = order_type,
												quantity = order_event.volume,
												price = order_event.target_price,          		# Precio límite
												stopPrice = order_event.sl,                 	# Precio de activación
												newClientOrderId = order_event.order_id,
												timeInForce = self.client.TIME_IN_FORCE_GTC)	# válido hasta que se cancele
		
		# Verifica el resultado de la ejecución de la orden 
		if self._check_execute_status(pending_order):
			
			print(f"Pending Order {order_event.signal} {order_event.target_order} para {order_event.symbol} de {order_event.volume} colacada en {order_event.target_price} correctamente.")
			self._create_put_execute_event(pending_order)
		else:
			print(f"Ha habido un error al ejecutar la orden {order_event.signal} para {order_event.symbol}")


	def _create_put_execute_event(self, order_result, ) -> None:
		
		execute_event = ExecutionEvent(symbol = order_result['symbol'],
									   signal = SignalType.BUY if order_result['side'] == self.client.SIDE_BUY else SignalType.SELL,
									   fill_price = order_result['fills'][0]['price'],    # REVISAR LOS PRECIOS CUANDO LA ORDEN SE HAGA EN VARIOS TRADES !!
									   fill_time = pd.to_datetime(order_result['transactTime'], unit='ms'),
									   volume = order_result['executedQty'])
		
		self.events_queue.put(execute_event)
	
	