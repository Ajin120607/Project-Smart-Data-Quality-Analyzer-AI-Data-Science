"""Interactive data cleaning endpoint."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.models import CleanRequest, CleanResponse
from app.services.session_store import session_store
from app.services.cleaning_service import clean_dataset

router = APIRouter(prefix="/api", tags=["Cleaning"])


@router.post("/clean", response_model=CleanResponse)
def apply_cleaning(clean_req: CleanRequest):
    """
    Applies selected cleaning operations on the active session's dataset copy.
    Generates a downloadable cleaned CSV artifact and returns before/after comparisons.
    """
    session_id = clean_req.session_id

    # Fallback to look up session_id from report_id if needed
    if not session_id and clean_req.report_id:
        report = session_store.get_report(clean_req.report_id)
        if report:
            session_id = report.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID or Report ID is required to perform dataset cleaning."
        )

    original_df = session_store.get_dataset(session_id)
    if original_df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active session expired or not found. Please re-upload your dataset."
        )

    session_entry = session_store._sessions.get(session_id, {})
    file_name = session_entry.get("file_name", "dataset.csv")

    _, response, _ = clean_dataset(
        original_df=original_df,
        clean_req=clean_req,
        file_name=file_name
    )

    return response
