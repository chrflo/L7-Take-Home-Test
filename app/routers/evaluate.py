from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, require_tenant
from app.schemas import EvaluateRequest, EvaluateResponse
from app.models import Flag
from app.services.flag_eval import evaluate_flag
from app.services.cache import TTLCache

router = APIRouter(prefix="/v1", tags=["evaluate"])
cache = TTLCache(ttl_seconds=15)

@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(body: EvaluateRequest, tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    cache_key = f"{tenant}:flag:{body.flag_key}"
    flag = cache.get(cache_key)
    if not flag:
        r = (await db.execute(select(Flag).where(Flag.tenant_id==tenant, Flag.key==body.flag_key))).scalar_one_or_none()
        if not r:
            raise HTTPException(status_code=404, detail="flag not found")
        flag = {"key": r.key, "state": r.state, "variants": r.variants, "rules": r.rules}
        cache.set(cache_key, flag)
    result = evaluate_flag(flag, tenant, body.user)
    return EvaluateResponse(**result)
