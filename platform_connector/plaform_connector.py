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

        # Comprueba el tipo de cuenta 
        self._live_account_warning()
    
    def _initialize_platform(self):
        """ 
        Conexión con la plataforma de Binance
        
        except:  Lanza un excepción si hay algun error al conectar con la plataforma
        Returns: None 
        """
        api_key = os.getenv('testnet_api_key')
        secret_key = os.getenv('testnet_secret_key')
        self.client = Client(api_key, secret_key, testnet=True)

        self.client.API_URL = "https://testnet.binance.vision/api"  # se establece url para api de pruebas "testnet"

        try:
            client_status = self.client.get_account_status()
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
        """
        Lanza una advertencia si el tipo de cuenta es live
        """

        if "https://api.binance.com/api" in self.client.API_URL:
            if not input('ALERTA! Cuenta de tipo REAL detectada. Capital en riesgo. ¿Deseas continuar? (y/n):').lower() == 'y':
                print('Base URL: ', self.client.API_URL)


                # BUSCAR EN LA API LA FUNCION PARA EL CIERRE DE SESION


                raise Exception("El usuario ha DETENIDO la conexion.")
            
        else:
            print("Estas en un entorno de pruebas (DEMO).")
            print('Base URL: ', self.client.API_URL)

        account_info = self.client.get_account()

        if 'accountType' in account_info:
            account_type = account_info['accountType']
            print(f'El tipo de cuenta es: {account_type}')
