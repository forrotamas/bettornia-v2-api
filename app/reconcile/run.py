from __future__ import annotations
from uuid import UUID
from typing import Any, Dict
import psycopg
from app.core.config import settings

def run_reconciliation(billing_account_id: UUID) -> tuple[UUID, Dict[str, Any]]:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")

    stats: Dict[str, Any] = {}

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select count(*) from bookmaker_live_attempts where billing_account_id=%s",
                (str(billing_account_id),),
            )
            stats["live_attempts_total"] = int(cur.fetchone()[0])

            cur.execute(
                "select count(*) from settlement_events where billing_account_id=%s",
                (str(billing_account_id),),
            )
            stats["settlement_events_total"] = int(cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from bookmaker_live_attempts la
                left join settlement_events se
                  on se.execution_id = la.execution_id
                 and se.billing_account_id = la.billing_account_id
                where la.billing_account_id=%s
                  and se.id is null
                """,
                (str(billing_account_id),),
            )
            stats["live_without_settlement"] = int(cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from settlement_events se
                left join bookmaker_live_attempts la
                  on la.execution_id = se.execution_id
                 and la.billing_account_id = se.billing_account_id
                where se.billing_account_id=%s
                  and la.id is null
                """,
                (str(billing_account_id),),
            )
            stats["settlement_without_live"] = int(cur.fetchone()[0])

            cur.execute(
                """
                insert into reconciliation_runs (billing_account_id, mode, status, stats_json, finished_at)
                values (%s, 'manual', 'COMPLETED', %s::jsonb, now())
                returning id
                """,
                (str(billing_account_id), psycopg.types.json.Json(stats)),
            )
            run_id = UUID(cur.fetchone()[0])

        conn.commit()

    return run_id, stats

def get_run(run_id: UUID) -> Dict[str, Any]:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required")

    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id, billing_account_id, mode, status, stats_json, error, started_at, finished_at
                from reconciliation_runs
                where id=%s
                """,
                (str(run_id),),
            )
            row = cur.fetchone()
            if not row:
                raise KeyError("RUN_NOT_FOUND")

            return {
                "id": str(row[0]),
                "billing_account_id": str(row[1]),
                "mode": row[2],
                "status": row[3],
                "stats": row[4],
                "error": row[5],
                "started_at": str(row[6]),
                "finished_at": str(row[7]) if row[7] else None,
            }
