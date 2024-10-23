from events.events import SizingEvent
from data_provider.data_provider import DataProvider
from ..interfaces.risk_manager_interface import IRiskManager
from ..properties.risk_manager_properties import MaxLeverageFactorRiskProps
import sys


class MaxLeverageFactorRiskManager(IRiskManager):

    def __init__(self, properties: MaxLeverageFactorRiskProps):
        self.max_leverage_factor = properties.max_leverage_factor

    
    def _compute_leverege_factor(self, data_provider: DataProvider, account_value_acc_ccy: float) -> float:
        
        account_equity = data_provider.get_account_balance_usdt()

        if account_equity <= 0:
            return sys.float_info.max
        else:
            return account_value_acc_ccy / account_equity
    

    def _check_new_position_is_compliant_with_max_leverege_factor(self, sizing_event: SizingEvent, current_position_value_acc_ccy: float, new_position_value_acc_ccy: float) -> bool:
        
        # calcula el nuevo expected account value que tendría la cuenta si ejecutamos la nueva posición
        new_account_value = current_position_value_acc_ccy + new_position_value_acc_ccy

        # CAlcula el nuevo factor de apalancamiento si se ejecuta esa posición
        new_leverage_factor = self._compute_leverege_factor(new_account_value)

        # Comprueba si el nuevo leverage factor sería mayor a nuestro máximo leverage factor
        if new_leverage_factor < self.max_leverage_factor: 
            return True
        else:
            print(f"RISK MANAGER: La posición {sizing_event.signal} {sizing_event.volume} implica un Leverage Factor de {new_leverage_factor},
                  que supera el máx. de {self.max_leverage_factor}")
            return False

    
    def asset_order(self, sizing_event: SizingEvent, current_position_value_acc_ccy: float, new_position_value_acc_ccy: float) -> float:

        # Método para hacer la función de discoteca (deja pasar la operación o no)
        if  self. _check_new_position_is_compliant_with_max_leverege_factor(sizing_event, current_position_value_acc_ccy, new_position_value_acc_ccy):
            return sizing_event.volume
        else:
            return 0.0
        
