from enum import Enum
from pydantic import BaseModel
import pandas as pd

# Define los distintios tipos de eventos

class EventType(str, Enum): # hereda de str y Enum
    DATA = "DATA"
    SIGNAL = "SIGNAL"


class SignalType(str, Enum): 
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class BaseEvent(BaseModel): 
    event_type:EventType

    class Config:
        arbitrary_types_allowed = True


class DataEvent(BaseEvent): 
    event_type: EventType = EventType.DATA
    symbol:str
    data:pd.Series


class SignalEvent(BaseEvent): 
    event_type: EventType = EventType.SIGNAL
    symbol: str
    signal: SignalType
    target_order: OrderType
    target_price: float
    order_id: int
    sl: float # stop loss
    tp: float # tipe profit


