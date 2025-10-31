import os

from fastapi import HTTPException, UploadFile, status

from backend.src.infrastructure.config.settings import rag_settings

# --- Configuration ---
MAX_FILE_SIZE_MB = rag_settings.MAX_FILE_SIZE_MB
ALLOWED_EXTENSIONS = rag_settings.ALLOWED_EXTENSIONS


async def validate_uploaded_file(file: UploadFile) -> None:
    """
    Validates an uploaded file for size and extension.
    Raises HTTPException if validation fails.
    """

    # --- 1️⃣ Check file name and extension ---
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a name."
        )

    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # --- 2️⃣ Read file content to validate size ---
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large ({size_mb:.2f} MB). "
            f"Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
        )

    # Reset file pointer after reading, so the file can be processed again later
    await file.seek(0)
