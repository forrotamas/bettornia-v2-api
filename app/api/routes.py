from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings
from app.domain.execution_plan import ExecutionPlan, AdapterContext
from app.adapters.registry import get as get_adapter, list_bookmakers
from app.execution.shadow_persist import persist_shadow_request

router = APIRouter()

class ShadowSubmitInput(BaseModel):
    plan: ExecutionPlan
    ctx: AdapterContext

@router.get("/health")
def health():
    return {
        "ok": True,
        "no_live": settings.no_live,
        "enable_shadow_submit": settings.enable_shadow_submit,
        "enable_live_submit": settings.enable_live_submit,
        "adapters": list_bookmakers(),
    }

@router.post("/shadow/submit")
def shadow_submit(inp: ShadowSubmitInput):
    if not settings.enable_shadow_submit:
        raise HTTPException(status_code=403, detail="SHADOW_SUBMIT_DISABLED")

    # Block 13/14 invariant: still shadow-only
    if not settings.no_live:
        raise HTTPException(status_code=400, detail="NO_LIVE must be enabled in shadow-only phases")

    try:
        adapter = get_adapter(inp.plan.bookmaker)
    except KeyError:
        raise HTTPException(status_code=400, detail="UNSUPPORTED_BOOKMAKER")

    req = adapter.build_request(inp.plan)

    persist_shadow_request(
        billing_account_id=inp.ctx.billing_account_id,
        execution_id=inp.plan.execution_id,
        bookmaker=inp.plan.bookmaker,
        request=req,
    )
    return {"persisted": True, "execution_id": str(inp.plan.execution_id), "schema": req.schema}
