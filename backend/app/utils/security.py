"""Security utilities for safe file handling, input sanitization, and token generation."""

import re
import uuid
from pathlib import Path
from fastapi import HTTPException, status

# 15 MB default maximum upload size limit to prevent memory exhaustion
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024


def generate_secure_id() -> str:
    """Generates an unpredictable UUID4 hex token."""
    return uuid.uuid4().hex


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to prevent directory traversal and special character injections."""
    if not filename:
        return "dataset.csv"
    
    # Strip any directory path components
    basename = Path(filename).name
    # Remove null bytes and non-printable characters
    clean_name = re.sub(r'[\x00-\x1f\x7f]', '', basename)
    # Allow alphanumeric, underscores, hyphens, and dots
    clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean_name)
    
    return clean_name


def validate_file_size(file_bytes: bytes, max_bytes: int = MAX_FILE_SIZE_BYTES) -> None:
    """Validates that file content does not exceed the allowed payload limit."""
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded CSV file is empty. Please upload a valid CSV file with data."
        )
    if len(file_bytes) > max_bytes:
        limit_mb = max_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed upload size limit of {limit_mb:.1f} MB."
        )
