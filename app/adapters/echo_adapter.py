from pydantic import BaseModel
from typing import Any, Dict
from app.domain.execution_plan import ExecutionPlan

class BookmakerRequest(BaseModel):
    bookmaker: str
    payload: Dict[str, Any]

class EchoAdapter:
    """
    Pure mapping: ExecutionPlan -> BookmakerRequest
    NO external calls. NO secrets/sessions. NO billing access from plan.
    """
    def build_request(self, plan: ExecutionPlan) -> BookmakerRequest:
        payload = {
            "execution_id": str(plan.execution_id),
            "currency": plan.currency,
            "stake": plan.stake,
            "selections": [s.model_dump() for s in plan.selections],
            "note": plan.note,
        }
        return BookmakerRequest(bookmaker=plan.bookmaker, payload=payload)
