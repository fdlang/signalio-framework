

class DataProvider():

    def __init__(self, client):
        self.client = client

    def get_latest_closed_bar(self, symbol:str, timeframe:str):
        self.client.get_klines()