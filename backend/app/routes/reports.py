"""Report retrieval endpoint."""

from fastapi import APIRouter, HTTPException, status
from app.services.session_store import session_store

router = APIRouter(prefix="/api", tags=["Reports"])


@router.get("/report/{report_id}")
def get_report_by_id(report_id: str):
    """Retrieves an existing quality audit report by its unique report ID."""
    report = session_store.get_report(report_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or has expired from the temporary session."
        )
    return report
