from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, List
from app.adapters.contract import BookmakerRequest
from app.domain.execution_plan import ExecutionPlan

class PinnacleLikeSelection(BaseModel):
    eventId: str
    market: str
    selection: str
    oddsDecimal: float = Field(gt=1.0)

class PinnacleLikePayload(BaseModel):
    oddsFormat: Literal["DECIMAL"] = "DECIMAL"
    currency: str = Field(min_length=3, max_length=3)
    stake: float = Field(gt=0)
    selections: List[PinnacleLikeSelection]

class PinnacleLikeAdapter:
    bookmaker = "pinnacle_like"
    schema = "pinnacle_like.v1"

    def build_request(self, plan: ExecutionPlan) -> BookmakerRequest:
        payload = PinnacleLikePayload(
            currency=plan.currency,
            stake=plan.stake,
            selections=[
                PinnacleLikeSelection(
                    eventId=s.event_id,
                    market=s.market,
                    selection=s.selection,
                    oddsDecimal=s.odds,
                )
                for s in plan.selections
            ],
        )
        return BookmakerRequest(
            bookmaker=self.bookmaker,
            schema=self.schema,
            payload=payload.model_dump(),
        )
