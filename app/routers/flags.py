from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, require_tenant
from app.schemas import FlagIn, FlagOut
from app.models import Flag
from app.services.audit import record_audit
from app.services.cache import TTLCache

router = APIRouter(prefix="/v1/flags", tags=["flags"])
cache = TTLCache(ttl_seconds=15)

@router.post("", response_model=FlagOut, status_code=status.HTTP_201_CREATED)
async def create_flag(body: FlagIn, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    # idempotent by (tenant, key)
    existing = (await db.execute(select(Flag).where(Flag.tenant_id==tenant, Flag.key==body.key))).scalar_one_or_none()
    if existing:
        # Update instead of duplicate
        before = {"description": existing.description, "state": existing.state, "variants": existing.variants, "rules": existing.rules}
        existing.description = body.description
        existing.state = body.state
        existing.variants = [v.model_dump() for v in body.variants]
        existing.rules = [r.model_dump() for r in body.rules]
        await db.commit()
        await record_audit(db, tenant, "system", "flag", body.key, "update", before, body.model_dump())
    else:
        f = Flag(tenant_id=tenant, key=body.key, description=body.description, state=body.state,
                 variants=[v.model_dump() for v in body.variants], rules=[r.model_dump() for r in body.rules])
        db.add(f)
        await db.commit()
        await record_audit(db, tenant, "system", "flag", body.key, "create", None, body.model_dump())
    cache.invalidate_prefix(f"{tenant}:flag:{body.key}")
    return FlagOut(**body.model_dump())

@router.get("", response_model=List[FlagOut])
async def list_flags(tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Flag).where(Flag.tenant_id==tenant))).scalars().all()
    outs = []
    for r in rows:
        outs.append(FlagOut(key=r.key, description=r.description, state=r.state, variants=r.variants, rules=r.rules))
    return outs

@router.get("/{key}", response_model=FlagOut)
async def get_flag(key: str, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Flag).where(Flag.tenant_id==tenant, Flag.key==key))).scalar_one_or_none()
    if not r: raise HTTPException(status_code=404, detail="flag not found")
    return FlagOut(key=r.key, description=r.description, state=r.state, variants=r.variants, rules=r.rules)

@router.put("/{key}", response_model=FlagOut)
async def update_flag(key: str, body: FlagIn, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Flag).where(Flag.tenant_id==tenant, Flag.key==key))).scalar_one_or_none()
    if not r: raise HTTPException(status_code=404, detail="flag not found")
    before = {"description": r.description, "state": r.state, "variants": r.variants, "rules": r.rules}
    r.description = body.description; r.state = body.state; r.variants = [v.model_dump() for v in body.variants]; r.rules = [x.model_dump() for x in body.rules]
    await db.commit()
    await record_audit(db, tenant, "system", "flag", key, "update", before, body.model_dump())
    cache.invalidate_prefix(f"{tenant}:flag:{key}")
    return FlagOut(**body.model_dump())

@router.delete("/{key}", status_code=204)
async def delete_flag(key: str, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Flag).where(Flag.tenant_id==tenant, Flag.key==key))).scalar_one_or_none()
    if not r: return
    await record_audit(db, tenant, "system", "flag", key, "delete", {"key": key}, None)
    await db.delete(r); await db.commit()
    cache.invalidate_prefix(f"{tenant}:flag:{key}")
