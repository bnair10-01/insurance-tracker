import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

CATEGORIES = ("auto", "home", "health", "life", "gadget", "travel", "pet", "other")
SOURCE_CHANNELS = ("email", "manual_upload", "telegram_upload")
PREMIUM_FREQUENCIES = ("monthly", "annual", "one-time")


def _in_list(column: str, values: tuple[str, ...]) -> str:
    return f"{column} IN (" + ", ".join(f"'{v}'" for v in values) + ")"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class InsuranceItem(Base):
    __tablename__ = "insurance_items"
    __table_args__ = (
        CheckConstraint(_in_list("category", CATEGORIES), name="ck_items_category"),
        CheckConstraint(_in_list("source_channel", SOURCE_CHANNELS), name="ck_items_source_channel"),
        CheckConstraint(
            f"premium_frequency IS NULL OR {_in_list('premium_frequency', PREMIUM_FREQUENCIES)}",
            name="ck_items_premium_frequency",
        ),
        Index("ix_items_user_category", "user_id", "category"),
        Index("ix_items_user_coverage_end", "user_id", "coverage_end"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)

    provider_phone: Mapped[str | None] = mapped_column(String(50))
    provider_email: Mapped[str | None] = mapped_column(String(255))
    provider_website: Mapped[str | None] = mapped_column(String(500))
    provider_agent_name: Mapped[str | None] = mapped_column(String(255))

    policy_number: Mapped[str | None] = mapped_column(String(100))
    coverage_start: Mapped[date] = mapped_column(Date, nullable=False)
    coverage_end: Mapped[date | None] = mapped_column(Date)

    premium_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    premium_frequency: Mapped[str | None] = mapped_column(String(20))

    coverage_summary: Mapped[str | None] = mapped_column(Text)

    source_channel: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="manual_upload"
    )
    source_document_ref: Mapped[str | None] = mapped_column(String(500))
    extraction_confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))

    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_verified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_extracted_text: Mapped[str | None] = mapped_column(Text)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
