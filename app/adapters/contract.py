from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, Protocol
from app.domain.execution_plan import ExecutionPlan

class BookmakerRequest(BaseModel):
    bookmaker: str
    schema: str  # e.g. "echo.v1", "pinnacle_like.v1"
    payload: Dict[str, Any]

class BookmakerAdapter(Protocol):
    bookmaker: str
    schema: str
    def build_request(self, plan: ExecutionPlan) -> BookmakerRequest: ...
