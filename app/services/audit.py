# app/services/audit.py  (Python 3.9 compatible)
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Audit


async def record_audit(
    db: AsyncSession,
    tenant: str,
    actor: str,
    entity: str,
    entity_key: str,
    action: str,
    before,
    after,
):
    a = Audit(
        tenant_id=tenant,
        actor=actor,
        entity=entity,
        entity_key=entity_key,
        action=action,
        before=before,
        after=after,
        ts=datetime.utcnow(),
    )
    db.add(a)
    await db.commit()


async def list_audit(
    db: AsyncSession,
    tenant: str,
    *,
    entity: Optional[str] = None,
    entity_key: Optional[str] = None,
    limit: int = 100,
):
    q = (
        select(Audit)
        .where(Audit.tenant_id == tenant)
        .order_by(Audit.ts.desc())
        .limit(limit)
    )
    if entity is not None:
        q = q.where(Audit.entity == entity)
    if entity_key is not None:
        q = q.where(Audit.entity_key == entity_key)
    rows = (await db.execute(q)).scalars().all()
    return [
        {
            "actor": r.actor,
            "entity": r.entity,
            "entity_key": r.entity_key,
            "action": r.action,
            "before": r.before,
            "after": r.after,
            "ts": r.ts.isoformat(),
        }
        for r in rows
    ]
