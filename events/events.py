from enum import Enum
from pydantic import BaseModel
import pandas as pd

# Define los distintios tipos de eventos

class EventType(str, Enum): # hereda de str y Enum
    DATA = "DATA"
    SIGNAL = "SIGNAL"


class BaseEvent(BaseModel): # hereda de BaseModel
    event_type:EventType

    class Config:
        arbitrary_types_allowed = True


class DataEvent(BaseEvent): # hereda de BaseEvent
    event_type: EventType = EventType.DATA
    symbol:str
    data:pd.Series

