from pydantic import BaseModel

class BaseSignalProps(BaseModel):
	pass

class MACrossoverProperties(BaseSignalProps):
	
	timeframe: str
	fast_period: int
	slow_period: int 

class RSIProperties(BaseSignalProps):
	
	timeframe: str
	rsi_period: int
	rsi_upper: float
	rsi_lower: float

class RsiMaCrossoverProperties(BaseSignalProps):
	
	rsi: RSIProperties
	ma_crossover:MACrossoverProperties