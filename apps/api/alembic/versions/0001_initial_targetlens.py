"""Create the TargetLens research, evidence, scoring and tutorial tables.

Revision ID: 0001_initial_targetlens
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_targetlens"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def uuid_column(name: str = "id", **kwargs: object) -> sa.Column[object]:
    return sa.Column(name, sa.Uuid(), nullable=False, **kwargs)


def upgrade() -> None:
    op.create_table(
        "research_session",
        uuid_column("id", primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("data_cutoff", sa.String(32), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_session_status", "research_session", ["status"])

    op.create_table(
        "session_message",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_session_message_session_id", "session_message", ["session_id"])
    op.create_index("ix_session_message_session_created", "session_message", ["session_id", "created_at"])

    op.create_table(
        "session_context",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "target_card_version",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("card", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "version", name="uq_target_card_session_version"),
    )
    op.create_index("ix_target_card_version_session_id", "target_card_version", ["session_id"])

    op.create_table(
        "decision_memo_version",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("memo", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "version", name="uq_decision_memo_session_version"),
    )
    op.create_index("ix_decision_memo_version_session_id", "decision_memo_version", ["session_id"])

    op.create_table(
        "score_snapshot",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_card_version_id", sa.Uuid(), sa.ForeignKey("target_card_version.id"), nullable=True),
        sa.Column("base_opportunity", sa.Float(), nullable=False),
        sa.Column("risk_burden", sa.Float(), nullable=False),
        sa.Column("evidence_confidence", sa.Float(), nullable=False),
        sa.Column("adjusted_score", sa.Float(), nullable=False),
        sa.Column("recommendation", sa.String(32), nullable=False),
        sa.Column("input_dimensions", sa.JSON(), nullable=False),
        sa.Column("redlines", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_score_snapshot_session_id", "score_snapshot", ["session_id"])

    op.create_table(
        "source_registry",
        uuid_column("id", primary_key=True),
        sa.Column("canonical_url", sa.String(2000), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("authority_tier", sa.String(32), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "source_snapshot",
        uuid_column("id", primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(128), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index("ix_source_snapshot_source_id", "source_snapshot", ["source_id"])

    op.create_table(
        "evidence_item",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_snapshot_id", sa.Uuid(), sa.ForeignKey("source_snapshot.id"), nullable=True),
        sa.Column("evidence_type", sa.String(64), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("locator", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_item_session_id", "evidence_item", ["session_id"])
    op.create_index("ix_evidence_item_session_type", "evidence_item", ["session_id", "evidence_type"])

    op.create_table(
        "claim",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_claim_session_id", "claim", ["session_id"])

    op.create_table(
        "claim_evidence",
        sa.Column("claim_id", sa.Uuid(), sa.ForeignKey("claim.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("evidence_item_id", sa.Uuid(), sa.ForeignKey("evidence_item.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    )

    op.create_table(
        "relation_fact",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("predicate", sa.String(128), nullable=False),
        sa.Column("object", sa.String(500), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
    )
    op.create_index("ix_relation_fact_session_id", "relation_fact", ["session_id"])

    op.create_table(
        "risk_event",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("mitigation", sa.Text(), nullable=True),
        sa.Column("requires_review", sa.Boolean(), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
    )
    op.create_index("ix_risk_event_session_id", "risk_event", ["session_id"])

    op.create_table(
        "tutorial_course",
        uuid_column("id", primary_key=True),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "tutorial_lesson",
        uuid_column("id", primary_key=True),
        sa.Column("course_id", sa.Uuid(), sa.ForeignKey("tutorial_course.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.UniqueConstraint("course_id", "position", name="uq_tutorial_lesson_position"),
    )
    op.create_index("ix_tutorial_lesson_course_id", "tutorial_lesson", ["course_id"])

    op.create_table(
        "tutorial_attempt",
        uuid_column("id", primary_key=True),
        sa.Column("course_id", sa.Uuid(), sa.ForeignKey("tutorial_course.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(120), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_tutorial_attempt_course_id", "tutorial_attempt", ["course_id"])

    op.create_table(
        "audit_log",
        uuid_column("id", primary_key=True),
        sa.Column("session_id", sa.Uuid(), sa.ForeignKey("research_session.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("entity_type", sa.String(120), nullable=False),
        sa.Column("entity_id", sa.String(120), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_session_id", "audit_log", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_session_id", table_name="audit_log")
    op.drop_table("audit_log")
    op.drop_index("ix_tutorial_attempt_course_id", table_name="tutorial_attempt")
    op.drop_table("tutorial_attempt")
    op.drop_index("ix_tutorial_lesson_course_id", table_name="tutorial_lesson")
    op.drop_table("tutorial_lesson")
    op.drop_table("tutorial_course")
    op.drop_index("ix_risk_event_session_id", table_name="risk_event")
    op.drop_table("risk_event")
    op.drop_index("ix_relation_fact_session_id", table_name="relation_fact")
    op.drop_table("relation_fact")
    op.drop_table("claim_evidence")
    op.drop_index("ix_claim_session_id", table_name="claim")
    op.drop_table("claim")
    op.drop_index("ix_evidence_item_session_type", table_name="evidence_item")
    op.drop_index("ix_evidence_item_session_id", table_name="evidence_item")
    op.drop_table("evidence_item")
    op.drop_index("ix_source_snapshot_source_id", table_name="source_snapshot")
    op.drop_table("source_snapshot")
    op.drop_table("source_registry")
    op.drop_index("ix_score_snapshot_session_id", table_name="score_snapshot")
    op.drop_table("score_snapshot")
    op.drop_index("ix_decision_memo_version_session_id", table_name="decision_memo_version")
    op.drop_table("decision_memo_version")
    op.drop_index("ix_target_card_version_session_id", table_name="target_card_version")
    op.drop_table("target_card_version")
    op.drop_table("session_context")
    op.drop_index("ix_session_message_session_created", table_name="session_message")
    op.drop_index("ix_session_message_session_id", table_name="session_message")
    op.drop_table("session_message")
    op.drop_index("ix_research_session_status", table_name="research_session")
    op.drop_table("research_session")
