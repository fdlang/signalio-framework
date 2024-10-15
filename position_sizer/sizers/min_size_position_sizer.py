from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer


class MinSizePositionSizer(IPositionSizer):

	def size_signal(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
		
		symbol_info = data_provider.client.get_symbol_info(signal_event.symbol)
		volume = symbol_info['filters'][1]['minQty']

		if volume is not None:
			return volume
		else: 
			print(f"ERROR (MinSizePositionSizer): No se ha podido determinar el volumen mínimo para {signal_event.symbol}")
			return 0.0
		
		