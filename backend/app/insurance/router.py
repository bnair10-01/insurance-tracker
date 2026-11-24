import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import InsuranceItem, User
from app.db.session import get_db
from app.insurance.schemas import Category, ItemCreate, ItemOut, ItemUpdate, Status, to_item_out
from app.storage import files

router = APIRouter(prefix="/api/items", tags=["items"])


async def _get_owned_item(item_id: uuid.UUID, user: User, db: AsyncSession) -> InsuranceItem:
    item = await db.scalar(
        select(InsuranceItem).where(
            InsuranceItem.id == item_id, InsuranceItem.user_id == user.id
        )
    )
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Insurance item not found")
    return item


@router.get("", response_model=list[ItemOut])
async def list_items(
    category: Category | None = Query(default=None),
    item_status: Status | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ItemOut]:
    query = select(InsuranceItem).where(InsuranceItem.user_id == current_user.id)
    if category is not None:
        query = query.where(InsuranceItem.category == category)
    query = query.order_by(InsuranceItem.date_added.desc())

    rows = (await db.scalars(query)).all()
    items = [to_item_out(row) for row in rows]
    if item_status is not None:
        items = [i for i in items if i.status == item_status]
    return items


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    return to_item_out(await _get_owned_item(item_id, current_user, db))


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = InsuranceItem(
        user_id=current_user.id,
        item_name=body.item_name,
        category=body.category,
        provider_name=body.provider_name,
        provider_phone=body.provider_contact.phone,
        provider_email=body.provider_contact.email,
        provider_website=body.provider_contact.website,
        provider_agent_name=body.provider_contact.agent_name,
        policy_number=body.policy_number,
        coverage_start=body.coverage_start,
        coverage_end=body.coverage_end,
        premium_amount=body.premium.amount,
        premium_frequency=body.premium.frequency,
        coverage_summary=body.coverage_summary,
        source_channel=body.source_channel,
        source_document_ref=body.source_document_ref,
        extraction_confidence=body.extraction_confidence,
        raw_extracted_text=body.raw_extracted_text,
        last_verified=datetime.now(timezone.utc),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return to_item_out(item)


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: uuid.UUID,
    body: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = await _get_owned_item(item_id, current_user, db)
    changes = body.model_dump(exclude_unset=True)

    if "provider_contact" in changes:
        contact = changes.pop("provider_contact") or {}
        item.provider_phone = contact.get("phone")
        item.provider_email = contact.get("email")
        item.provider_website = contact.get("website")
        item.provider_agent_name = contact.get("agent_name")

    if "premium" in changes:
        premium = changes.pop("premium") or {}
        item.premium_amount = premium.get("amount")
        item.premium_frequency = premium.get("frequency")

    for field, value in changes.items():
        setattr(item, field, value)

    item.last_verified = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    return to_item_out(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    item = await _get_owned_item(item_id, current_user, db)
    ref = item.source_document_ref
    await db.delete(item)
    await db.commit()
    if ref:
        files.delete_file(current_user.id, ref)


@router.get("/{item_id}/document")
async def download_document(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    item = await _get_owned_item(item_id, current_user, db)
    if not item.source_document_ref:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No document stored for this item")

    path = files.resolve_path(current_user.id, item.source_document_ref)
    if path is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Stored document is missing")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"{item.item_name}.pdf",
    )
