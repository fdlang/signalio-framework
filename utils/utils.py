from binance.client import Client

# Método estatico para poder convertir una divisa a otra

class Utils():

    def __init__(self):
        pass

    @staticmethod
    def convert_currency_amount_to_another_currency(amount: float, from_ccy: str, to_ccy: str) -> float:

        all_fx_symbol = set()
        exchange_info = Client().get_exchange_info()

        for symbol_info in exchange_info['symbols']:
            all_fx_symbol.add(symbol_info['symbol'])

        from_ccy = from_ccy.upper()
        to_ccy = to_ccy.upper()

        # Buscar el símbolo de cambio
        fx_symbol_candidates = [symbol for symbol in all_fx_symbol if from_ccy in symbol and to_ccy in symbol]
        
        if not fx_symbol_candidates:
            raise ValueError(f"No se encontraron símbolos de cambio para {from_ccy} a {to_ccy}")

        fx_symbol = fx_symbol_candidates[0]

        try:
            # Obtener el último precio del ticker
            tick = Client().get_ticker(symbol=fx_symbol)

            if tick is None:
                raise ValueError(f"El símbolo {fx_symbol} no está disponible en la plataforma Binance.")

            last_price = float(tick['bidPrice'])

            # Determinar la base del símbolo
            if fx_symbol.endswith('USDT'):
                fx_symbol_base = fx_symbol[:-4]  
            elif fx_symbol.endswith('BTC'):
                fx_symbol_base = fx_symbol[:-3]  
            else:
                raise ValueError(f"El símbolo {fx_symbol} no es válido.")

            # Convierte la cantidad de la divisa origen a la divisa destino
            if fx_symbol_base == to_ccy:
                convert_amount = amount * last_price  # Convierte a la divisa base
            else:
                convert_amount = amount / last_price  # Convierte a USDT o BTC

            return convert_amount

        except Exception as e:
            print(f"ERROR: No se pudo recuperar el último símbolo {fx_symbol}. Exception: {e}")
            return 0.0
    

    @staticmethod
    def get_usdt_value(tickers: dict, asset: str, amount: float) -> float:

        if asset == 'USDT': 
            return amount
        
        if asset == 'NFT' or asset == '1000PEPPER':
            return 0.0
        
        try:
            ticker = tickers.get(f"{asset}USDT")
            price_in_usdt = float(ticker['price'])  

            return price_in_usdt * amount
        
        except Exception as e:
            print(f"No se pudo obtener el precio de {asset} en USDT. Exception: {e}")
            return 0.0