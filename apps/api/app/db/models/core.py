from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchSession(Base):
    __tablename__ = "research_session"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200))
    question: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", index=True)
    data_cutoff: Mapped[str] = mapped_column(String(32))
    mode: Mapped[str] = mapped_column(String(32), default="mock")
    owner_id: Mapped[UUID | None] = mapped_column(ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True, index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class UserAccount(Base):
    __tablename__ = "user_account"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuthSession(Base):
    __tablename__ = "auth_session"
    __table_args__ = (Index("ix_auth_session_token_hash", "token_hash"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_account.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SessionMessage(Base):
    __tablename__ = "session_message"
    __table_args__ = (Index("ix_session_message_session_created", "session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text())
    citations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SessionContext(Base):
    __tablename__ = "session_context"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), unique=True)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class TargetCardVersion(Base):
    __tablename__ = "target_card_version"
    __table_args__ = (UniqueConstraint("session_id", "version", name="uq_target_card_session_version"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer())
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")
    card: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DecisionMemoVersion(Base):
    __tablename__ = "decision_memo_version"
    __table_args__ = (UniqueConstraint("session_id", "version", name="uq_decision_memo_session_version"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer())
    memo: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ScoreSnapshot(Base):
    __tablename__ = "score_snapshot"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    target_card_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("target_card_version.id"), nullable=True)
    base_opportunity: Mapped[float] = mapped_column(Float())
    risk_burden: Mapped[float] = mapped_column(Float())
    evidence_confidence: Mapped[float] = mapped_column(Float())
    adjusted_score: Mapped[float] = mapped_column(Float())
    recommendation: Mapped[str] = mapped_column(String(32))
    input_dimensions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    redlines: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SourceRegistry(Base):
    __tablename__ = "source_registry"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    canonical_url: Mapped[str] = mapped_column(String(2000), unique=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64))
    authority_tier: Mapped[str] = mapped_column(String(32))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SourceSnapshot(Base):
    __tablename__ = "source_snapshot"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    source_id: Mapped[UUID] = mapped_column(ForeignKey("source_registry.id", ondelete="CASCADE"), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    content_hash: Mapped[str] = mapped_column(String(128))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class EvidenceItem(Base):
    __tablename__ = "evidence_item"
    __table_args__ = (Index("ix_evidence_item_session_type", "session_id", "evidence_type"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    source_snapshot_id: Mapped[UUID | None] = mapped_column(ForeignKey("source_snapshot.id"), nullable=True)
    evidence_type: Mapped[str] = mapped_column(String(64))
    claim: Mapped[str] = mapped_column(Text())
    excerpt: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence: Mapped[float] = mapped_column(Float(), default=0)
    locator: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    claim_text: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    claim_id: Mapped[UUID] = mapped_column(ForeignKey("claim.id", ondelete="CASCADE"), primary_key=True)
    evidence_item_id: Mapped[UUID] = mapped_column(ForeignKey("evidence_item.id", ondelete="CASCADE"), primary_key=True)


class RelationFact(Base):
    __tablename__ = "relation_fact"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    predicate: Mapped[str] = mapped_column(String(128))
    object: Mapped[str] = mapped_column(String(500))
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)


class KnowledgeGraphFact(Base):
    """Reusable, first-party graph facts built from normalized research runs.

    ``RelationFact`` remains session-scoped for audit history.  This table is
    the durable TargetLens graph library: a later question can reuse a
    previously observed relation without exposing the graph as a UI card.
    """

    __tablename__ = "knowledge_graph_fact"
    __table_args__ = (UniqueConstraint("target_key", "subject", "predicate", "object", name="uq_knowledge_graph_fact_relation"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    target_key: Mapped[str] = mapped_column(String(200), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    subject_label: Mapped[str] = mapped_column(String(500))
    subject_type: Mapped[str] = mapped_column(String(64))
    predicate: Mapped[str] = mapped_column(String(128))
    object: Mapped[str] = mapped_column(String(500))
    object_label: Mapped[str] = mapped_column(String(500))
    object_type: Mapped[str] = mapped_column(String(64))
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    source_connectors: Mapped[list[str]] = mapped_column(JSON, default=list)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class RiskEvent(Base):
    __tablename__ = "risk_event"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("research_session.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text())
    mitigation: Mapped[str | None] = mapped_column(Text(), nullable=True)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list)


class TutorialCourse(Base):
    __tablename__ = "tutorial_course"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text())
    published: Mapped[bool] = mapped_column(Boolean, default=False)


class TutorialLesson(Base):
    __tablename__ = "tutorial_lesson"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_tutorial_lesson_position"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("tutorial_course.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer())
    title: Mapped[str] = mapped_column(String(200))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class TutorialAttempt(Base):
    __tablename__ = "tutorial_attempt"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("tutorial_course.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="IN_PROGRESS")
    score: Mapped[float | None] = mapped_column(Float(), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID | None] = mapped_column(ForeignKey("research_session.id", ondelete="SET NULL"), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str] = mapped_column(String(120))
    entity_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
