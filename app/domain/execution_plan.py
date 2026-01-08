from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from uuid import UUID

class ExecutionSelection(BaseModel):
    event_id: str
    market: str
    selection: str
    odds: float

class ExecutionPlan(BaseModel):
    execution_id: UUID
    bookmaker: str
    currency: str = Field(min_length=3, max_length=3)
    stake: float = Field(gt=0)
    selections: List[ExecutionSelection]
    # NOTE: billing_account_id is NOT part of ExecutionPlan by design.
    note: Optional[str] = None

class AdapterContext(BaseModel):
    # Explicit context passed by runner/service, not read from plan
    billing_account_id: UUID
