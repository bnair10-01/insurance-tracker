from datetime import date

from pydantic import BaseModel, Field

from app.insurance.schemas import Category, Premium, ProviderContact


class ExtractionDraft(BaseModel):
    item_name: str | None = None
    category: Category | None = None
    provider_name: str | None = None
    provider_contact: ProviderContact = ProviderContact()
    policy_number: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    premium: Premium = Premium()
    coverage_summary: str | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    source_document_ref: str
    raw_extracted_text: str
