from data_provider.data_provider import DataProvider


class Portfolio():

    def __init__(self, order_id: int, data_provider: DataProvider):
        self.order_id = order_id
        self.data = data_provider


    def get_open_position(self) -> tuple:
        return tuple(self.data.client.get_open_orders())


    def get_strategy_open_position(self) -> tuple:

        positions = []
        
        for position in self.data.client.get_open_orders():
            if position['clientOrderId'] == self.order_id:
                positions.append(position)
        
        return tuple(positions)
    

    def get_number_of_open_position_by_symbol(self, symbol: str) -> dict[str, int]:

        longs = 0
        shorts = 0

        for position in self.data.client.get_open_orders(symbol= symbol):
            if position['type'] == self.data.client.SIDE_BUY:
                longs += 1
            else:
                shorts += 1
        
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}
    

    def get_number_of_strategy_open_position_by_symbol(self, symbol: str) -> dict[str, int]:

        longs = 0
        shorts = 0

        for position in self.data.client.get_open_orders(symbol= symbol):
            if position['clientOrderId'] == self.order_id:
                longs += 1
            else:
                shorts += 1
        
        return {"LONG": longs, "SHORT": shorts, "TOTAL": longs + shorts}


