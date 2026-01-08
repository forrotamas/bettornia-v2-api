import json
from datetime import datetime, timezone
from uuid import UUID
from app.db.conn import get_conn
from app.adapters.echo_adapter import BookmakerRequest

def persist_shadow_request(
    *,
    billing_account_id: UUID,
    execution_id: UUID,
    bookmaker: str,
    request: BookmakerRequest,
) -> None:
    now = datetime.now(timezone.utc)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bookmaker_shadow_requests
                  (billing_account_id, execution_id, bookmaker, request_json, created_at)
                VALUES
                  (%s, %s, %s, %s::jsonb, %s)
                """,
                (
                    str(billing_account_id),
                    str(execution_id),
                    bookmaker,
                    json.dumps(request.model_dump()),
                    now,
                ),
            )
        conn.commit()
