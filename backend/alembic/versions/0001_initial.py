"""initial schema: users + insurance_items

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

CATEGORIES = "'auto', 'home', 'health', 'life', 'gadget', 'travel', 'pet', 'other'"
SOURCE_CHANNELS = "'email', 'manual_upload', 'telegram_upload'"
PREMIUM_FREQUENCIES = "'monthly', 'annual', 'one-time'"


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    op.create_table(
        "users",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "insurance_items",
        sa.Column("id", PGUUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", PGUUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("provider_name", sa.String(255), nullable=False),
        sa.Column("provider_phone", sa.String(50)),
        sa.Column("provider_email", sa.String(255)),
        sa.Column("provider_website", sa.String(500)),
        sa.Column("provider_agent_name", sa.String(255)),
        sa.Column("policy_number", sa.String(100)),
        sa.Column("coverage_start", sa.Date, nullable=False),
        sa.Column("coverage_end", sa.Date),
        sa.Column("premium_amount", sa.Numeric(12, 2)),
        sa.Column("premium_frequency", sa.String(20)),
        sa.Column("coverage_summary", sa.Text),
        sa.Column("source_channel", sa.String(20), nullable=False, server_default="manual_upload"),
        sa.Column("source_document_ref", sa.String(500)),
        sa.Column("extraction_confidence", sa.Numeric(3, 2)),
        sa.Column("date_added", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_verified", sa.DateTime(timezone=True)),
        sa.Column("raw_extracted_text", sa.Text),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f"category IN ({CATEGORIES})", name="ck_items_category"),
        sa.CheckConstraint(f"source_channel IN ({SOURCE_CHANNELS})", name="ck_items_source_channel"),
        sa.CheckConstraint(
            f"premium_frequency IS NULL OR premium_frequency IN ({PREMIUM_FREQUENCIES})",
            name="ck_items_premium_frequency",
        ),
    )
    op.create_index("ix_insurance_items_user_id", "insurance_items", ["user_id"])
    op.create_index("ix_items_user_category", "insurance_items", ["user_id", "category"])
    op.create_index("ix_items_user_coverage_end", "insurance_items", ["user_id", "coverage_end"])


def downgrade() -> None:
    op.drop_table("insurance_items")
    op.drop_table("users")
