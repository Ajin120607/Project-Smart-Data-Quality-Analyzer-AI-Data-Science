"""Duplicate row detection and inspection engine."""

import math
from typing import Any, Dict, List
import pandas as pd
from app.schemas.models import DuplicateAnalysis


def clean_record_for_json(record: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = {}
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            cleaned[k] = None
        elif pd.isna(v):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def analyze_duplicates(df: pd.DataFrame) -> DuplicateAnalysis:
    """
    Identifies completely duplicated rows in the dataset and extracts
    sample records for user inspection.
    """
    total_rows = len(df)
    if total_rows == 0:
        return DuplicateAnalysis(
            duplicate_row_count=0,
            duplicate_percentage=0.0,
            total_rows=0,
            unique_rows=0,
            sample_duplicates=[]
        )

    # Flag duplicate rows (keep='first' flags subsequent occurrences)
    is_duplicate = df.duplicated(keep="first")
    duplicate_count = int(is_duplicate.sum())
    duplicate_pct = round((duplicate_count / total_rows) * 100, 2)
    unique_rows = total_rows - duplicate_count

    # Extract sample duplicate rows for inspection (up to 15 samples)
    duplicate_rows_df = df[df.duplicated(keep=False)].head(15)
    
    # Convert NaNs to None for valid JSON serialization
    sample_records: List[Dict[str, Any]] = [
        clean_record_for_json(r) for r in duplicate_rows_df.to_dict(orient="records")
    ]

    return DuplicateAnalysis(
        duplicate_row_count=duplicate_count,
        duplicate_percentage=duplicate_pct,
        total_rows=total_rows,
        unique_rows=unique_rows,
        sample_duplicates=sample_records
    )
