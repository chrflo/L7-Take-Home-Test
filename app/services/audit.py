# app/services/audit.py
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Audit

async def record_audit(db: AsyncSession, tenant: str, actor: str, entity: str, entity_key: str, action: str, before, after):
    # TODO: persist audit entries
    return

async def list_audit(db: AsyncSession, tenant: str, *, entity: Optional[str]=None, entity_key: Optional[str]=None, limit: int=100):
    # TODO: query & filter audit log
    raise NotImplementedError("audit listing not implemented")
