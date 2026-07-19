"""Add local accounts, opaque auth sessions and session ownership.

Existing records are marked as demo-visible so a local upgrade does not hide
the research history that was already created before account support existed.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_auth_and_session_ownership"
down_revision: Union[str, None] = "0002_knowledge_graph_library"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_account",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_user_account_email", "user_account", ["email"])

    op.create_table(
        "auth_session",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user_account.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_auth_session_user_id", "auth_session", ["user_id"])
    op.create_index("ix_auth_session_token_hash", "auth_session", ["token_hash"])
    op.create_index("ix_auth_session_expires_at", "auth_session", ["expires_at"])

    op.add_column("research_session", sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.add_column("research_session", sa.Column("is_demo", sa.Boolean(), server_default=sa.true(), nullable=False))
    op.create_foreign_key("fk_research_session_owner", "research_session", "user_account", ["owner_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_research_session_owner_id", "research_session", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_research_session_owner_id", table_name="research_session")
    op.drop_constraint("fk_research_session_owner", "research_session", type_="foreignkey")
    op.drop_column("research_session", "is_demo")
    op.drop_column("research_session", "owner_id")
    op.drop_index("ix_auth_session_expires_at", table_name="auth_session")
    op.drop_index("ix_auth_session_token_hash", table_name="auth_session")
    op.drop_index("ix_auth_session_user_id", table_name="auth_session")
    op.drop_table("auth_session")
    op.drop_index("ix_user_account_email", table_name="user_account")
    op.drop_table("user_account")
