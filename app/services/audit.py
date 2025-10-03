from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Audit
from datetime import datetime

async def record_audit(db: AsyncSession, tenant: str, actor: str, entity: str, entity_key: str, action: str, before, after):
    a = Audit(tenant_id=tenant, actor=actor, entity=entity, entity_key=entity_key, action=action, before=before, after=after, ts=datetime.utcnow())
    db.add(a)
    await db.commit()

async def list_audit(db: AsyncSession, tenant: str, *, entity: str | None = None, entity_key: str | None = None, limit: int = 100):
    from sqlalchemy import and_
    q = select(Audit).where(Audit.tenant_id == tenant).order_by(Audit.ts.desc()).limit(limit)
    if entity:
        q = q.where(Audit.entity == entity)
    if entity_key:
        q = q.where(Audit.entity_key == entity_key)
    rows = (await db.execute(q)).scalars().all()
    return [{
        "actor": r.actor, "entity": r.entity, "entity_key": r.entity_key, "action": r.action, "before": r.before, "after": r.after, "ts": r.ts.isoformat()
    } for r in rows]
