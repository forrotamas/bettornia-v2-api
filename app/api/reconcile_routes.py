from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from app.reconcile.run import run_reconciliation, get_run

router = APIRouter()

class ReconcileRunInput(BaseModel):
    billing_account_id: UUID

@router.post("/reconcile/run")
def reconcile_run(inp: ReconcileRunInput):
    run_id, stats = run_reconciliation(inp.billing_account_id)
    return {"run_id": str(run_id), "stats": stats}

@router.get("/reconcile/run/{run_id}")
def reconcile_get(run_id: UUID):
    try:
        return get_run(run_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")
