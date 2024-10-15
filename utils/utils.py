from binance.client import Client

# Método estatico para poder convertir una divisa a otra

class Utils():

    def __init__(self):
        pass

    @staticmethod
    def convert_currency_amount_to_another_currency(amount: float, from_ccy: str, to_ccy: str) -> float:
        
        all_fx_symbol = ("ADAUSDT","ADABTC", "SOLUSDT", "SOLBTC", "FETUSDT", "FETBTC", "INJUSDT", "INJBTC", "LINKUSDT", "LINKBTC", 
                         "SHIBUSDT", "SHIBBTC", "POLUSDT", "POLBTC", "VETUSDT", "VETBTC", "CFXUSDT", "CFXBTC", "ICPUSDT", "ICPBTC", 
                         "CHZUSDT", "CHZBTC", "ROSEUSDT", "ROSEBTC", "LINAUSDT", "LINABTC", "HOTUSDT", "HOTBTC", "RSRUSDT", "RSRBTC",
                         "IOTAUSDT", "IOTABTC", "WINUSDT", "WINBTC", "DOGEUSDT", "DOGEBTC")
        
        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        fx_symbol = [symbol for symbol in all_fx_symbol if from_ccy in symbol and to_ccy in symbol][0]  
        fx_symbol_base = ()

        for symbol in fx_symbol:
            if symbol.endswith('USDT'): 
                fx_symbol_base = symbol[:-4]
            elif symbol.endswith('BTC'):
                fx_symbol_base = symbol[:-3]
            else:
                continue

            fx_symbol_base.add(fx_symbol_base)

        try:
            tick = Client().get_ticker(symbol=fx_symbol)

            if tick is None:
                raise (f"El símbolo {fx_symbol} no está disponible en la plataforma Binance. Por favor, revisa los símbolos disponibles.")
        except Exception as e:
            print(f"ERROR: No se pudo recuperar el último símbolo {fx_symbol}. Exception: {e}")
            return 0.0
        
        else:
            last_price = float(tick['bidPrice'])

            # Convierte la cantidad de la divisa origen a la divisa destino
            convert_amount = amount / last_price if fx_symbol_base == to_ccy else amount = last_price
            return convert_amount
    

    @staticmethod
    def get_usdt_value(asset, amount):

        if asset == 'USDT':  # Si la moneda es USDT, no hace falta convertir
            return float(amount)
        
        try:
            # Obtiene el precio de la moneda en USDT
            ticker = Client().get_symbol_ticker(symbol=f"{asset}USDT")
            price_in_usdt = float(ticker['price'])           
            return price_in_usdt * float(amount)
        
        except Exception as e:
            # Si no existe un par directo en USDT, se ignora
            print(f"No se pudo obtener el precio de {asset} en USDT. Exception: {e}")
            return 0