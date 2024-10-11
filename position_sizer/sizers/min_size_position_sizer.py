from data_provider.data_provider import DataProvider
from events.events import SignalEvent
from ..interfaces.position_sizer_interface import IPositionSizer


class MinSizePositionSizer(IPositionSizer):

	def size_position(self, signal_event: SignalEvent, data_provider: DataProvider) -> float:
		
		symbol_info = data_provider.client.get_symbol_Info(signal_event.symbol)
		symbol_info_filters = symbol_info['filters']

		for fliter in symbol_info_filters:
			if fliter['filterType'] == 'LOT_SIZE':
				vol_minQty = fliter['minQty']

		if vol_minQty is not None:
			return vol_minQty
		else: 
			print(f"ERROR (MinSizePositionSizer): No se ha podido determinar el volumen mínimo para {vol_minQty}")
			return 0.0
		
		