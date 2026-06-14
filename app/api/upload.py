import logging

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.upload import UploadResponse
from app.services.file_storage import store_upload_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    stored_name, size = await store_upload_file(
        upload_dir=settings.UPLOAD_DIR,
        file=file,
        max_size_bytes=settings.MAX_UPLOAD_SIZE_BYTES,
        allowed_content_types=settings.ALLOWED_UPLOAD_TYPES,
    )
    logger.info(
        "File uploaded | user_id=%d | original='%s' | stored='%s' | size=%d",
        current_user.id,
        file.filename,
        stored_name,
        size,
    )
    return {
        "filename": stored_name,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size": size,
        "path": f"{settings.UPLOAD_DIR}/{stored_name}",
    }
