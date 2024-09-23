import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv, find_dotenv

class PlatformConnector():
    def __init__(self):

        # busca el archivo .env y carga sus valores
        load_dotenv(find_dotenv())

        # Inicialización de la plataforma
        self._initialize_platform()
    
    def _initialize_platform(self):
        """ 
        Conexión con la plataforma de Binance
        
        except:  Lanza un excepción si hay algun error al conectar con la plataforma
        Returns: None 
        """
        api_key = os.getenv('api_key')
        secret_key = os.getenv('secret_key')
        client = Client(api_key, secret_key, testnet=True) # testnet = cuenta para puebas si es true

        try:
            client_status = client.get_account_status()
            status_value = client_status['data']

            if status_value == 'Normal':
                print('La conexión con Binance se ha lanzado con éxito')
        
        except BinanceAPIException as e:
            print(f'Error de la API de Binance: {e}')
        except BinanceRequestException as e:
            print(f'Error de conexión: {e}')
        except Exception as e:
            print(f'Error inesperado: {e}')

    def _live_account_warning(self) -> None:
        Client.get_account()  # revisar en que cuenta esta si live o pruebas