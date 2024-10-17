import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv, find_dotenv

class PlatformConnector():
	def __init__(self, symbols:list):

		
		# Inicialización de la plataforma
		self.client = self._initialize_platform()

		# Comprueba el tipo de cuenta 
		self._live_account_warning()

		# Imprime información de la cuenta
		self._print_account_info()

		# Comprobación del trading algoritmico
		self._check_algo_trading_enable()

		# Verificación de existencia de símbolos en el MarketWatch
		self._symbols_to_marketwatch(symbols)
 

	def _initialize_platform(self):
		""" 
		Conexión con la plataforma de Binance
		
		except:  Lanza un excepción si hay algun error al conectar con la plataforma
		Returns: Cliente de Binance 
		"""

		# busca el archivo .env y carga sus valores
		load_dotenv(find_dotenv())
		api_key = os.getenv('api_key')
		secret_key = os.getenv('secret_key')

		client = Client(api_key, secret_key)

		try:
			client_status = client.get_account_status()
			status_value = client_status['data']

			if status_value == 'Normal':
				print('La conexión con Binance se ha lanzado con éxito')
		
		except BinanceAPIException as e:
			print(f'Error de la API de Binance: {e}')

			if e.code == 1021:
				print(f"Hay un problema de sincronización de tiempo entre tu máquina local y los servidores de Binance. Sincroniza el reloj de tu máquina.")
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
		
		else:
			if "https://api.binance.com/api" in self.client.API_URL:
				confirmar = input('ALERTA! Cuenta de tipo REAL detectada. Capital en riesgo. ¿Deseas continuar? (y/n):').lower()
				
				if confirmar != 'y':
					self._switch_to_testnet()   
					print("El usuario ha DETENIDO la conexion.\nEntorno de puebas (DEMO) activado.")  
				else:
					print("Entorno LIVE activado.") 
			
				print('Base URL: ', self.client.API_URL)


	def _switch_to_testnet(self):
		"""Cambia la conexión a testnet y limpia las credenciales."""
		self._clear_credentials()
		self.api_key = os.getenv('testnet_api_key')
		self.secret_key = os.getenv('testnet_secret_key')
		self.client = Client(self.api_key, self.secret_key, testnet=True)
		self.client.API_URL = "https://testnet.binance.vision/api"    


	def _clear_credentials(self):
		"""Limpia las credenciales de la memoria."""
		
		self.api_key = None
		self.secret_key = None


	def _check_algo_trading_enable(self) -> None:
		
		# Comprueba que el trading algoritmico está activado.
		if self.client.API_URL == 'https://api.binance.com/api':
			trading_status = self.client.get_account_api_trading_status()

			if trading_status['data']['isLocked']:
				raise Exception(f"El trading algorítmico está desactivado. Por favor actívalo MANUALMENTE!")
			else:
				print(f"El trading algoritmico esta habilitado.")


	def _symbols_to_marketwatch(self, symbols: list) -> None:
		"""
		Verifica si los símbolos en la lista están en el estado 'TRADING' dentro de exchange_info.
		Si el símbolo no está en estado 'TRADING', imprime un mensaje indicándolo.
		"""
		exchange_info = self.client.get_exchange_info()

		for symbol in symbols:
			found = False 
			for symbol_info in exchange_info['symbols']:
				if symbol_info['symbol'] == symbol:
					found = True
					if symbol_info['status'] != 'TRADING':
						print(f"El símbolo {symbol} no está en estado 'TRADING'")
					else:
						print(f"El símbolo {symbol} se encuentra en el MarketWatch!")
					break  # Salimos del bucle una vez que encontramos el símbolo

			if not found:
				print(f"El símbolo {symbol} no existe en el MarketWatch.")


	def _account_balance(self, balance:dict):

		bal_info = set()

		for bal in balance['balances']:
				asset = str(bal['asset'])
				free = float(bal['free'])
				locked = float(bal['locked'])

				if free > 0 or locked > 0:
					bal_info.add((asset, free, locked))

		return bal_info


	def _print_account_info(self):
		"""Obtiene y muestra información de la cuenta."""

		try:
			account_info = self.client.get_account()
				
			print(f'\n+---------- INFORMACIÓN DE LA CUENTA ----------\n')
			print(f"| - Comisión Maker: {account_info['makerCommission']}")
			print(f"| - Comisión Taker: {account_info['takerCommission']}")
			print(f"| - Puede operar: {account_info['canTrade']}")
			print(f"| - Puede retirar: {account_info['canWithdraw']}")
			print(f"| - Puede depositar: {account_info['canDeposit']}")
			print(f"| - Tipo de cuenta: {account_info['accountType']}")
			print(f"| - ID de usuario: {account_info['uid']}")
			print(f'\n+----------------------------------------------\n')

			print(f"------------ Balance de la cuenta ------------\n")
			for bal in self._account_balance(account_info):
				print(f'| - Activo: {bal[0]}, Disponible: {bal[1]}, Bloqueado: {bal[2]}')

			print("\n+----------------------------------------------\n")	
		except BinanceAPIException as e: 
			print(f'Error al obtener información de la cuenta: {e}')
	
	

	   
			  
		

