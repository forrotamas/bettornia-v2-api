from __future__ import annotations
from uuid import UUID
from typing import Any, Dict, Optional
import psycopg
from app.core.config import settings

def persist_live_attempt(
    billing_account_id: UUID,
    execution_id: UUID,
    bookmaker: str,
    request: Any,
    status: str,
    reason: Optional[str] = None,
) -> None:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")

    # request is a Pydantic model (BookmakerRequest)
    req_json: Dict[str, Any] = request.model_dump()

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookmaker_live_attempts
                  (billing_account_id, execution_id, bookmaker, request_json, status, reason)
                VALUES
                  (%s, %s, %s, %s::jsonb, %s, %s)
                """,
                (
                    str(billing_account_id),
                    str(execution_id),
                    bookmaker,
                    psycopg.types.json.Json(req_json),
                    status,
                    reason,
                ),
            )
        conn.commit()
