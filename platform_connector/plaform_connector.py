import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv, find_dotenv

class PlatformConnector():
    def __init__(self):

        # busca el archivo .env y carga sus valores
        load_dotenv(find_dotenv())
        self.api_key = os.getenv('api_key')
        self.secret_key = os.getenv('secret_key')

        # Inicialización de la plataforma
        self.client = self._initialize_platform()

        # Comprueba el tipo de cuenta 
        self._live_account_warning()

        # Comprobación del trading algoritmico
        self._check_algo_trading_enable()

        # self._add_symbols_to_marketwatch()
    

    def _initialize_platform(self):
        """ 
        Conexión con la plataforma de Binance
        
        except:  Lanza un excepción si hay algun error al conectar con la plataforma
        Returns: Cliente de Binance 
        """

        client = Client(self.api_key, self.secret_key)

        try:
            client_status = client.get_account_status()
            status_value = client_status['data']

            if status_value == 'Normal':
                print('La conexión con Binance se ha lanzado con éxito')
        
        except BinanceAPIException as e:
            print(f'Error de la API de Binance: {e}')
            return None
        except BinanceRequestException as e:
            print(f'Error de conexión: {e}')
            return None
        except Exception as e:
            print(f'Error inesperado: {e}')
            return None
        
        return client


    def _live_account_warning(self) -> None:
        """
        Lanza una advertencia si el tipo de cuenta es live.
        Si el usuario no desea continuar, cambia la cuenta a la testnet.
        """

        if self.client is None:
            print("Error: Cliente de Binance no inicializado correctamente.")
            return

        if "https://api.binance.com/api" in self.client.API_URL:
            confirmar = input('ALERTA! Cuenta de tipo REAL detectada. Capital en riesgo. ¿Deseas continuar? (y/n):').lower()
            
            if confirmar != 'y':
                self._switch_to_testnet()   
            else:
                print("Entorno LIVE activado.") 
        
        print('Base URL: ', self.client.API_URL)
        
        # Verifica la información de la cuenta
        self._get_account_info()


    def _switch_to_testnet(self):
        """Cambia la conexión a testnet y limpia las credenciales."""
        self._clear_credentials()
        self.api_key = os.getenv('testnet_api_key')
        self.secret_key = os.getenv('testnet_secret_key')
        self.client = Client(self.api_key, self.secret_key, testnet=True)
        self.client.API_URL = "https://testnet.binance.vision/api"
        print("El usuario ha DETENIDO la conexion.\nEntorno de puebas (DEMO) activado.")      


    def _get_account_info(self):
        """Obtiene y muestra información de la cuenta."""

        try:
            account_info = self.client.get_account()
            if 'accountType' in account_info:
                account_type = account_info['accountType']
                print(f'El tipo de cuenta es: {account_type}')
        except BinanceAPIException as e:
            print(f'Error al obtener información de la cuenta: {e}')


    def _clear_credentials(self):
        """Limpia las credenciales de la memoria."""
        
        self.api_key = None
        self.secret_key = None


    def _check_algo_trading_enable(self) -> None:
        
        # Comprueba que el trading algoritmico está activado.
        if self.client.API_URL == 'https://api.binance.com/api':
            trading_status = self.client.get_account_api_trading_status()

            if not trading_status['data']['isLocked']:
                raise Exception("El trading algorítmico está desactivado. Por favor actívalo MANUALMENTE!")
            else:
                print('El trading algoritmico esta habilitado.')
        else:
            self._add_symbols_to_marketwatch(self.client.get_exchange_info())


    def _add_symbols_to_marketwatch(self, symbols:list) -> None:
        """
        """

        assets = set() # crea un conjunto vacio para evitar duplicados

        for symbols_info in symbols['symbols']:
            if symbols_info['status'] == 'TRADING':
                assets.add(symbols_info['symbol'])
            else:
                print(f"No se ha podido añadir el simbolo {symbols_info['symbol']} al MarketWatch: {symbols_info['status']}")
        
        print(sorted(assets))


            
        
