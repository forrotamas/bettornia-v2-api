from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.domain.execution_plan import ExecutionPlan, AdapterContext
from app.adapters.echo_adapter import EchoAdapter
from app.execution.shadow_persist import persist_shadow_request

router = APIRouter()

class ShadowSubmitInput(BaseModel):
    plan: ExecutionPlan
    ctx: AdapterContext

@router.get("/health")
def health():
    return {"ok": True, "no_live": settings.no_live}

@router.post("/shadow/submit")
def shadow_submit(inp: ShadowSubmitInput):
    if not settings.no_live:
        raise HTTPException(status_code=400, detail="NO_LIVE must be enabled for shadow-only mode")

    adapter = EchoAdapter()
    req = adapter.build_request(inp.plan)

    persist_shadow_request(
        billing_account_id=inp.ctx.billing_account_id,
        execution_id=inp.plan.execution_id,
        bookmaker=inp.plan.bookmaker,
        request=req,
    )
    return {"persisted": True, "execution_id": str(inp.plan.execution_id)}
