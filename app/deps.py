from typing import AsyncGenerator, Annotated
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.db_dsn, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

Tenant = Annotated[str, Header(alias="X-Tenant-ID")]

def require_tenant(tenant: Tenant):
    if not tenant:
        raise HTTPException(status_code=400, detail="X-Tenant-ID required")
    return tenant
