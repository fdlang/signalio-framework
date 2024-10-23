from pydantic import BaseModel


class BaseRiskProps(BaseModel):
    pass


class MaxLeverageFactorRiskProps(BaseRiskProps):
    max_leverage_factor: float