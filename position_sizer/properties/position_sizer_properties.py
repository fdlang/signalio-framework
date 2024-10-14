from pydantic import BaseModel


class MinSizingProps(BaseModel):
    pass


class FixedSizingProps(BaseModel):
    volume: float


class RiskPctSizingProps(BaseModel):
    risk_pct: float