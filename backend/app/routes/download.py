"""Cleaned dataset artifact download endpoint."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from app.services.session_store import session_store

router = APIRouter(prefix="/api", tags=["Download"])


@router.get("/download/{file_id}")
def download_cleaned_file(file_id: str):
    """
    Downloads a previously generated cleaned CSV file.
    Enforces secure identifier lookup and returns standard attachment headers.
    """
    artifact = session_store.get_download(file_id)
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested download artifact not found or has expired."
        )

    filename = artifact["file_name"]
    content = artifact["content"]

    return Response(
        content=content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
