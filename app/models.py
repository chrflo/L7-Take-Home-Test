# app/models.py (excerpt)
from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Text, JSON, DateTime,
    UniqueConstraint, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

Base = declarative_base()


class Flag(Base):
    """
    Feature flag definition scoped to a tenant.

    - Uniqueness: (tenant_id, key) must be unique.
    - Variants: list of {key, weight} used for default distribution (A/B/n).
    - Rules: ordered list of targeting rules; each may force a variant or apply percentage rollout.
    - Soft delete: optional deleted_at; deleted flags should not evaluate/list by default.
    """
    __tablename__ = "flags"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_flags_tenant_key"),
        Index("ix_flags_tenant_state", "tenant_id", "state"),
        CheckConstraint("state IN ('on','off')", name="ck_flags_state"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True,
        comment="Surrogate numeric identifier"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False,
        comment="Tenant namespace identifier; all reads/writes scoped by this"
    )
    key: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Flag key, unique per tenant (e.g., 'checkout_new')"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Human-readable description of purpose/scope"
    )
    state: Mapped[str] = mapped_column(
        String(8), default="off", nullable=False,
        comment="'on' or 'off'; gates rule evaluation"
    )
    variants: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False,
        comment="List of {key, weight}; weights normalized during evaluation"
    )
    rules: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False,
        comment="Ordered rules; e.g., {'id':'r1','when':{'attr':{'role':'employee'}},'rollout':{'variant':'treatment'}}"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True,
        comment="Soft-delete marker; hide from reads/evaluation when set"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="Creation time (UTC)"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
        comment="Last update time (UTC)"
    )


class Segment(Base):
    """
    Reusable cohort definition for targeting rules (e.g., 'ca_ios_new_users').

    - Uniqueness: (tenant_id, key) must be unique.
    - Criteria: JSON matcher tree; your evaluator interprets this (doc your shape).
    """
    __tablename__ = "segments"
    __table_args__ = (
        UniqueConstraint("tenant_id", "key", name="uq_segments_tenant_key"),
        Index("ix_segments_tenant", "tenant_id"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True,
        comment="Surrogate numeric identifier"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False,
        comment="Tenant namespace identifier"
    )
    key: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Segment key, unique per tenant (e.g., 'ca_ios_new_users')"
    )
    criteria: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False,
        comment="Matcher tree; e.g., {'all':[{'attr':{'country':'CA'}},{'attr':{'os':'iOS'}}]}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False,
        comment="Creation time (UTC)"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False,
        comment="Last update time (UTC)"
    )


class Audit(Base):
    """
    Immutable audit log of changes for compliance and debugging.

    - Write-only: append on create/update/delete.
    - Indexed by (tenant_id, ts) for fast recent-first queries.
    """
    __tablename__ = "audit"
    __table_args__ = (
        Index("ix_audit_tenant_ts", "tenant_id", "ts"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True,
        comment="Surrogate numeric identifier"
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False,
        comment="Tenant namespace identifier"
    )
    actor: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Who performed the change (service/client id or user id)"
    )
    entity: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="Entity type: 'flag' or 'segment'"
    )
    entity_key: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="Stable key of the entity within the tenant"
    )
    action: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="Action verb: 'create' | 'update' | 'delete'"
    )
    before: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        comment="Selected fields before change (or null on create)"
    )
    after: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True,
        comment="Selected fields after change (or null on delete)"
    )
    ts: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, index=True, nullable=False,
        comment="Event timestamp (UTC)"
    )
