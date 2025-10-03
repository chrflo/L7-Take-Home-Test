from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_db, require_tenant
from app.services.audit import list_audit

router = APIRouter(prefix="/v1/audit", tags=["audit"])

@router.get("")
async def list_audit_entries(tenant: str = Depends(require_tenant), db: AsyncSession = Depends(get_db)):
    return await list_audit(db, tenant)
