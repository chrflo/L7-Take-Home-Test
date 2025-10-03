from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.deps import get_db, require_tenant
from app.schemas import EvaluateRequest, EvaluateResponse
from app.models import Flag
from app.services.flag_eval import evaluate_flag
from app.services.cache import TTLCache

router = APIRouter(prefix="/v1", tags=["evaluate"])
cache = TTLCache(ttl_seconds=15)

@router.post("/evaluate", response_model=EvaluateResponse, status_code=status.HTTP_200_OK)
async def evaluate(_: EvaluateRequest, tenant: str = Depends(require_tenant)):
    """
    TODO (candidate):
    - Load flag by (tenant, flag_key) from DB (or cache; add TTL cache)
    - Call app.services.flag_eval.evaluate_flag(flag, tenant, body.user)
    - Return EvaluateResponse with variant/reason/rule_id/details
    - Handle 404 when flag is missing
    """
    raise HTTPException(status_code=501, detail="Not implemented")