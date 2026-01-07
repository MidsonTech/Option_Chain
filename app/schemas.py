from pydantic import BaseModel
from typing import List

class OptionRequest(BaseModel):
    symbol: str
    expiry: str
    strike: float
    spot_range: List[float]



class VixScenarioRequest(BaseModel):
    symbol: str
    expiry: str
    strike: float
    spot_range: List[float]
    vix_range: List[float]


class VixScenarioRequest1(BaseModel):
    symbol: str
    expiry: str            
    strike: float
    spot_range: List[float]
    vix_range: List[float] = []  
