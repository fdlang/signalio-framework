from portfolio.portfolio import Portfolio
from events.events import OrderEvent, ExecutionEvent, SignalType, PlacePendingOrderEvent
from platform_connector.plaform_connector import PlatformConnector
import pandas as pd

from queue import Queue


class SpotOrderExecutor():

	def __init__(self, events_queue: Queue, portfolio: Portfolio, connector: PlatformConnector):

		self.events_queue = events_queue
		self.PORTFOLIO = portfolio
		self.client = connector.client


	def excute_order(self, order_event: OrderEvent) -> None:

		# Evalua el tipo de orden que se quiere ejecutar y llama al método
		if order_event.target_order == "MARKET":
			self._execute_market_order_spot(order_event)
		else:
			self._send_pending_order_spot(order_event)

	
	def _execute_market_order_spot(self, order_event: OrderEvent) -> None:

		# comprueba si la orden es de venta o compra
		if order_event.signal == "BUY" :
			order_side = self.client.SIDE_BUY
		elif order_event.signal == "SELL":
			order_side = self.client.SIDE_SELL
		else:
			raise Exception(f"SPOT ORDER EXECUTOR: La señal {order_event.signal} no es válida.")
		
		market_order = self.client.create_order(symbol=order_event.symbol,
												side=order_side,
												type=self.client.ORDER_TYPE_MARKET,
												quantity=order_event.volume,
												newClientOrderId = order_event.order_id)

		# Verifica el resultado de la ejecución de la orden 
		if self._check_execute_status(market_order):
			print(f"Spot Market Order: {order_event.signal} para {order_event.symbol} de {order_event.volume} ejecutado correctamente.")
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
	

	def _send_pending_order_spot(self, order_event: OrderEvent) -> None:

		# comprueba si es de tipo STOP_LOSS o LIMIT
		if order_event.target_order == self.client.ORDER_TYPE_STOP_LOSS_LIMIT:
			
			order_type = self.client.ORDER_TYPE_STOP_LOSS_LIMIT
			specific_params = {"stopPrice": order_event.sl}		# Precio de activación
		
		elif order_event.target_order == self.client.ORDER_TYPE_STOP_LOSS:
			order_type = self.client.ORDER_TYPE_STOP_LOSS
			specific_params = {"stopPrice": order_event.sl} 	

		elif order_event.target_order == self.client.ORDER_TYPE_LIMIT:

			order_type = self.client.ORDER_TYPE_LIMIT
			specific_params = {} 

		else:
			raise Exception(f"SPOT ORDER EXECUTE: La orden pendiente objetivo {order_event.target_order} no es válida.")
		
		# Define los parametros
		side_type = self.client.SIDE_BUY if order_event.signal == "BUY" else self.client.SIDE_SELL
		orders_params = {
			"symbol": order_event.symbol,
			"side": side_type,
			"type": order_type,
			"quantity": order_event.volume,
			"price": order_event.target_price, 					# Precio límite 
			"newClientOrderId": order_event.order_id,
			"timeInForce": self.client.TIME_IN_FORCE_GTC 		# válido hasta que se cancele
		}	

		orders_params.update(specific_params)	
		pending_order = self.client.create_order(**orders_params)													
		
		# Verifica el resultado de la ejecución de la orden 
		if self._check_execute_status(pending_order):
			
			print(f"Spot Pending Order: {order_event.signal} {order_event.target_order} para {order_event.symbol} de {order_event.volume} colacada en {order_event.target_price} correctamente.")
			self._create_put_place_pending_order_event(order_event)
		else:
			print(f"Ha habido un error al ejecutar la orden {order_event.signal} para {order_event.symbol}")


	def cancel_pending_order_by_symbol_and_id(self, symbol, order_id) -> None:

		order = self.client.get_open_orders(symbol=symbol)

		if order is None:
			print(f"SPOT ORDER EXECUTE: No existe ninguna orden pendiente parfa el symbolo {symbol}")
			return

		for key in order:
			if key['orderId'] == order_id:
				cancel_order = self.client.cancel_order(symbol=symbol, orderId=order_id)

			# Verifica el resultado de la cancelacion de la orden 
			if self._check_execute_status(cancel_order):
				print(f"Orden pendiente para symbol: {symbol} con id: {order_id} y volumen: {key['']}, se ha cancelado correctamente,.")
			else:
				print(f"Ha habido un error al ejecutar la orden {order_id} para {symbol}")


	def _create_put_execute_event(self, order_result ) -> None:
		
		execute_event = ExecutionEvent(symbol = order_result['symbol'],
									   signal = SignalType.BUY if order_result['side'] == self.client.SIDE_BUY else SignalType.SELL,
									   fill_price = order_result['fills'][0]['price'],    # REVISAR LOS PRECIOS CUANDO LA ORDEN SE HAGA EN VARIOS TRADES !!
									   fill_time = pd.to_datetime(order_result['transactTime'], unit='ms'),
									   volume = order_result['executedQty'])
		
		self.events_queue.put(execute_event)
	

	def _create_put_place_pending_order_event(self, order_event: OrderEvent) -> None:

		placed_order_event = PlacePendingOrderEvent(symbol= order_event.symbol,
													signal= order_event.signal,
													target_order= order_event.target_order,
													target_price= order_event.target_price,
													order_id= order_event.order_id,
													sl= order_event.sl, 
													tp= order_event.tp, 
													volume= order_event.volume)
		
		self.events_queue.put(placed_order_event)