import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.db.models import InsuranceItem
from app.insurance.status import compute_status

Category = Literal["auto", "home", "health", "life", "gadget", "travel", "pet", "other"]
SourceChannel = Literal["email", "manual_upload", "telegram_upload"]
PremiumFrequency = Literal["monthly", "annual", "one-time"]
Status = Literal["active", "upcoming", "expiring_soon", "expired", "unknown"]


class ProviderContact(BaseModel):
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    agent_name: str | None = None


class Premium(BaseModel):
    amount: float | None = None
    frequency: PremiumFrequency | None = None


class ItemCreate(BaseModel):
    item_name: str = Field(min_length=1, max_length=255)
    category: Category
    provider_name: str = Field(min_length=1, max_length=255)
    provider_contact: ProviderContact = ProviderContact()
    policy_number: str | None = None
    coverage_start: date
    coverage_end: date | None = None
    premium: Premium = Premium()
    coverage_summary: str | None = None
    source_channel: SourceChannel = "manual_upload"
    source_document_ref: str | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    raw_extracted_text: str | None = None


class ItemUpdate(BaseModel):
    item_name: str | None = Field(default=None, min_length=1, max_length=255)
    category: Category | None = None
    provider_name: str | None = Field(default=None, min_length=1, max_length=255)
    provider_contact: ProviderContact | None = None
    policy_number: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    premium: Premium | None = None
    coverage_summary: str | None = None


class ItemOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    item_name: str
    category: Category
    provider_name: str
    provider_contact: ProviderContact
    policy_number: str | None
    coverage_start: date
    coverage_end: date | None
    premium: Premium
    coverage_summary: str | None
    status: Status
    source_channel: SourceChannel
    source_document_ref: str | None
    extraction_confidence: float | None
    date_added: datetime
    last_verified: datetime | None
    raw_extracted_text: str | None


def to_item_out(item: InsuranceItem) -> ItemOut:
    return ItemOut(
        id=item.id,
        user_id=item.user_id,
        item_name=item.item_name,
        category=item.category,
        provider_name=item.provider_name,
        provider_contact=ProviderContact(
            phone=item.provider_phone,
            email=item.provider_email,
            website=item.provider_website,
            agent_name=item.provider_agent_name,
        ),
        policy_number=item.policy_number,
        coverage_start=item.coverage_start,
        coverage_end=item.coverage_end,
        premium=Premium(
            amount=float(item.premium_amount) if item.premium_amount is not None else None,
            frequency=item.premium_frequency,
        ),
        coverage_summary=item.coverage_summary,
        status=compute_status(item.coverage_start, item.coverage_end),
        source_channel=item.source_channel,
        source_document_ref=item.source_document_ref,
        extraction_confidence=(
            float(item.extraction_confidence) if item.extraction_confidence is not None else None
        ),
        date_added=item.date_added,
        last_verified=item.last_verified,
        raw_extracted_text=item.raw_extracted_text,
    )
