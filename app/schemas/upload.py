from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str = Field(..., description="Stored filename")
    original_filename: str = Field(..., description="Original uploaded filename")
    content_type: str = Field(..., description="Detected MIME type")
    size: int = Field(..., description="File size in bytes")
    path: str = Field(..., description="Relative storage path")
