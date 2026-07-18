"""Persist the reusable TargetLens knowledge-graph library.

Revision ID: 0002_knowledge_graph_library
Revises: 0001_initial_targetlens
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_knowledge_graph_library"
down_revision: Union[str, None] = "0001_initial_targetlens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_graph_fact",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("target_key", sa.String(length=200), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("subject_label", sa.String(length=500), nullable=False),
        sa.Column("subject_type", sa.String(length=64), nullable=False),
        sa.Column("predicate", sa.String(length=128), nullable=False),
        sa.Column("object", sa.String(length=500), nullable=False),
        sa.Column("object_label", sa.String(length=500), nullable=False),
        sa.Column("object_type", sa.String(length=64), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("source_connectors", sa.JSON(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("target_key", "subject", "predicate", "object", name="uq_knowledge_graph_fact_relation"),
    )
    op.create_index("ix_knowledge_graph_fact_target_key", "knowledge_graph_fact", ["target_key"])


def downgrade() -> None:
    op.drop_index("ix_knowledge_graph_fact_target_key", table_name="knowledge_graph_fact")
    op.drop_table("knowledge_graph_fact")
