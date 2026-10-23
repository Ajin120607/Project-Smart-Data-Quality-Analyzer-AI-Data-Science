"""Dataset upload and data quality analysis endpoint."""

from typing import List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
import json

from app.schemas.models import QualityReport
from app.utils.security import sanitize_filename, validate_file_size
from app.utils.csv_parser import parse_csv_bytes
from app.services.session_store import session_store
from app.services.analysis_engine import generate_quality_report

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze", response_model=QualityReport)
async def analyze_dataset(
    file: UploadFile = File(...),
    outlier_method: str = Form("iqr"),
    selected_columns: Optional[str] = Form(None)
):
    """
    Accepts an uploaded CSV file, executes comprehensive data quality analysis,
    and returns a full quality audit report.
    """
    raw_filename = file.filename or ""
    # 1. Validate file extension strictly
    if not raw_filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only comma-separated value (.csv) files are supported."
        )

    clean_filename = sanitize_filename(raw_filename)

    # 2. Read and validate content size
    try:
        content = await file.read()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read the uploaded file stream."
        )

    validate_file_size(content)
    file_size_kb = round(len(content) / 1024, 2)

    # 3. Parse CSV into DataFrame
    df, detected_enc = parse_csv_bytes(content, clean_filename)

    # 4. Parse selected columns if provided as JSON string
    cols_to_analyze = None
    if selected_columns:
        try:
            parsed = json.loads(selected_columns)
            if isinstance(parsed, list) and len(parsed) > 0:
                cols_to_analyze = [c for c in parsed if c in df.columns]
        except Exception:
            pass

    # 5. Store dataset in session
    session_id = session_store.store_dataset(df, clean_filename)

    # 6. Generate quality report
    report = generate_quality_report(
        df=df,
        file_name=clean_filename,
        file_size_kb=file_size_kb,
        session_id=session_id,
        outlier_method=outlier_method,
        selected_columns=cols_to_analyze
    )

    # Store report for session retrieval using model_dump(mode="json")
    session_store.store_report(report.report_id, session_id, report.model_dump(mode="json"))

    return report
