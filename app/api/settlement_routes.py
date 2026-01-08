from fastapi import APIRouter
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Any, Dict, Optional, Literal
from app.settlement.persist import ingest_settlement_event

router = APIRouter()

class SettlementIngestInput(BaseModel):
    billing_account_id: UUID
    execution_id: UUID
    source: str = "manual"
    outcome: Literal["WIN","LOSS","VOID","REFUND","CASHOUT","PARTIAL"]
    settled_stake: float = Field(ge=0)
    settled_payout: float = Field(ge=0)
    external_ref: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

@router.post("/settlement/ingest")
def settlement_ingest(inp: SettlementIngestInput):
    ingest_settlement_event(
        billing_account_id=inp.billing_account_id,
        execution_id=inp.execution_id,
        source=inp.source,
        outcome=inp.outcome,
        settled_stake=inp.settled_stake,
        settled_payout=inp.settled_payout,
        external_ref=inp.external_ref,
        raw=inp.raw,
    )
    return {"ingested": True, "execution_id": str(inp.execution_id)}
