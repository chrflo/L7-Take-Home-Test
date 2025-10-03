from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, require_tenant
from app.schemas import SegmentIn, SegmentOut
from app.models import Segment
from app.services.audit import record_audit
from app.services.cache import TTLCache

router = APIRouter(prefix="/v1/segments", tags=["segments"])
cache = TTLCache(ttl_seconds=15)

@router.post("", response_model=SegmentOut, status_code=status.HTTP_201_CREATED)
async def create_segment(body: SegmentIn, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(Segment).where(Segment.tenant_id==tenant, Segment.key==body.key))).scalar_one_or_none()
    if existing:
        before = {"criteria": existing.criteria}
        existing.criteria = body.criteria
        await db.commit()
        await record_audit(db, tenant, "system", "segment", body.key, "update", before, body.criteria)
    else:
        s = Segment(tenant_id=tenant, key=body.key, criteria=body.criteria)
        db.add(s); await db.commit()
        await record_audit(db, tenant, "system", "segment", body.key, "create", None, body.criteria)
    cache.invalidate_prefix(f"{tenant}:segment:{body.key}")
    return SegmentOut(**body.model_dump())

@router.get("", response_model=List[SegmentOut])
async def list_segments(tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Segment).where(Segment.tenant_id==tenant))).scalars().all()
    return [SegmentOut(key=r.key, criteria=r.criteria) for r in rows]

@router.get("/{key}", response_model=SegmentOut)
async def get_segment(key: str, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Segment).where(Segment.tenant_id==tenant, Segment.key==key))).scalar_one_or_none()
    if not r: raise HTTPException(status_code=404, detail="segment not found")
    return SegmentOut(key=r.key, criteria=r.criteria)
