from __future__ import annotations
from app.adapters.contract import BookmakerRequest
from app.domain.execution_plan import ExecutionPlan

class EchoAdapter:
    bookmaker = "echo"
    schema = "echo.v1"

    def build_request(self, plan: ExecutionPlan) -> BookmakerRequest:
        payload = {
            "execution_id": str(plan.execution_id),
            "currency": plan.currency,
            "stake": plan.stake,
            "selections": [s.model_dump() for s in plan.selections],
            "note": plan.note,
        }
        return BookmakerRequest(bookmaker=self.bookmaker, schema=self.schema, payload=payload)
