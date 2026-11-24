import uuid
from pathlib import Path

from app.config import settings

UPLOADS_ROOT = Path(settings.uploads_dir).resolve()


def save_upload(user_id: uuid.UUID, data: bytes) -> str:
    user_dir = UPLOADS_ROOT / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"{uuid.uuid4()}.pdf"
    path.write_bytes(data)
    return str(path.relative_to(UPLOADS_ROOT))


def resolve_path(user_id: uuid.UUID, ref: str) -> Path | None:
    """Resolve a stored ref to an on-disk path, refusing anything outside the user's own dir."""
    user_dir = (UPLOADS_ROOT / str(user_id)).resolve()
    candidate = (UPLOADS_ROOT / ref).resolve()
    if not candidate.is_relative_to(user_dir) or not candidate.is_file():
        return None
    return candidate


def delete_file(user_id: uuid.UUID, ref: str) -> None:
    path = resolve_path(user_id, ref)
    if path is not None:
        path.unlink(missing_ok=True)
