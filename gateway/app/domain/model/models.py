from pydantic import BaseModel
from typing import Dict, Any, List

class TitanicRequest(BaseModel):
    data: List[Dict[str, Any]]

class TitanicUpdateRequest(BaseModel):
    passenger_id: int
    updates: Dict[str, Any] 