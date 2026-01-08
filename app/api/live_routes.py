from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.core.config import settings
from app.domain.execution_plan import ExecutionPlan, AdapterContext
from app.adapters.registry import get as get_adapter
from app.execution.live_persist import persist_live_attempt

router = APIRouter()

class LiveSubmitInput(BaseModel):
    plan: ExecutionPlan
    ctx: AdapterContext

@router.post("/live/submit")
def live_submit(inp: LiveSubmitInput, x_live_arm: str | None = Header(default=None)):
    # Hard kill-switch always wins
    if settings.no_live:
        persist_live_attempt(inp.ctx.billing_account_id, inp.plan.execution_id, inp.plan.bookmaker, get_adapter(inp.plan.bookmaker).build_request(inp.plan), "BLOCKED", "NO_LIVE")
        raise HTTPException(status_code=403, detail="NO_LIVE")

    if not settings.enable_live_submit:
        persist_live_attempt(inp.ctx.billing_account_id, inp.plan.execution_id, inp.plan.bookmaker, get_adapter(inp.plan.bookmaker).build_request(inp.plan), "BLOCKED", "LIVE_SUBMIT_DISABLED")
        raise HTTPException(status_code=403, detail="LIVE_SUBMIT_DISABLED")

    if not settings.live_arm_token:
        raise HTTPException(status_code=500, detail="LIVE_ARM_TOKEN_NOT_CONFIGURED")

    if x_live_arm != settings.live_arm_token:
        raise HTTPException(status_code=403, detail="LIVE_NOT_ARMED")

    # Still no external call in Block 15: only persist attempt as PENDING
    adapter = get_adapter(inp.plan.bookmaker)
    req = adapter.build_request(inp.plan)
    persist_live_attempt(inp.ctx.billing_account_id, inp.plan.execution_id, inp.plan.bookmaker, req, "PENDING", None)
    return {"accepted": True, "execution_id": str(inp.plan.execution_id), "schema": req.schema}
