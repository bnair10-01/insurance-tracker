from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth.dependencies import get_current_user
from app.config import settings
from app.db.models import User
from app.extraction import claude_extractor, pdf_text
from app.extraction.schemas import ExtractionDraft
from app.storage import files

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _parse_date(value) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value.strip()[:10])
    except ValueError:
        return None


@router.post("/extract", response_model=ExtractionDraft)
async def extract_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> ExtractionDraft:
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF files are supported")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File exceeds the {settings.max_upload_mb}MB limit",
        )

    raw_text = pdf_text.extract_text_from_pdf(pdf_bytes)
    if not raw_text:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No text could be read from this PDF. It may be a scanned image.",
        )

    saved_ref = files.save_upload(current_user.id, pdf_bytes)
    extracted = await claude_extractor.extract_insurance_details(raw_text)

    return ExtractionDraft(
        item_name=extracted.get("item_name"),
        category=extracted.get("category"),
        provider_name=extracted.get("provider_name"),
        provider_contact=extracted.get("provider_contact") or {},
        policy_number=extracted.get("policy_number"),
        coverage_start=_parse_date(extracted.get("coverage_start")),
        coverage_end=_parse_date(extracted.get("coverage_end")),
        premium=extracted.get("premium") or {},
        coverage_summary=extracted.get("coverage_summary"),
        extraction_confidence=extracted.get("extraction_confidence"),
        source_document_ref=saved_ref,
        raw_extracted_text=raw_text,
    )
