from __future__ import annotations
from uuid import UUID
from typing import Any, Dict, Optional
import psycopg
from app.core.config import settings

def ingest_settlement_event(
    billing_account_id: UUID,
    execution_id: UUID,
    source: str,
    outcome: str,
    settled_stake: float,
    settled_payout: float,
    external_ref: Optional[str],
    raw: Optional[Dict[str, Any]],
) -> None:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO settlement_events
                  (billing_account_id, execution_id, source, outcome, settled_stake, settled_payout, external_ref, raw_json)
                VALUES
                  (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    str(billing_account_id),
                    str(execution_id),
                    source,
                    outcome,
                    settled_stake,
                    settled_payout,
                    external_ref,
                    psycopg.types.json.Json(raw) if raw is not None else psycopg.types.json.Json(None),
                ),
            )
        conn.commit()
