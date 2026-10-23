"""Missing value detection and recommendation engine."""

from typing import List, Tuple
import pandas as pd
import numpy as np
from app.schemas.models import MissingAnalysis, MissingColumnDetail

PLACEHOLDER_MISSING_STRINGS = {
    "", "nan", "null", "none", "n/a", "na", "?", "-", "undefined", "<na>"
}


def analyze_missing_values(df: pd.DataFrame) -> MissingAnalysis:
    """
    Identifies missing values across the dataset, accounting for both standard
    NaN/None values and common placeholder strings like 'N/A', 'null', or '?'.
    """
    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return MissingAnalysis(
            total_missing_cells=0,
            missing_cell_percentage=0.0,
            columns_with_missing=0,
            by_column=[]
        )

    by_column_details: List[MissingColumnDetail] = []
    total_missing_cells = 0
    columns_with_missing = 0

    for col in df.columns:
        series = df[col]
        # Standard pandas nulls
        is_standard_null = series.isna()
        
        # String placeholder nulls
        is_string_null = pd.Series(False, index=series.index)
        if series.dtype == object or pd.api.types.is_string_dtype(series):
            is_string_null = series.astype(str).str.strip().str.lower().isin(PLACEHOLDER_MISSING_STRINGS)

        combined_missing = is_standard_null | is_string_null
        missing_count = int(combined_missing.sum())
        total_missing_cells += missing_count

        if missing_count > 0:
            columns_with_missing += 1

        missing_pct = round((missing_count / len(df)) * 100, 2)

        # Determine severity and recommendation
        if missing_pct == 0:
            severity = "none"
            rec = "No missing values detected. Column is complete."
        elif missing_pct < 5:
            severity = "low"
            if pd.api.types.is_numeric_dtype(series):
                rec = f"Low missingness ({missing_pct}%). Consider mean/median imputation or removing affected rows."
            else:
                rec = f"Low missingness ({missing_pct}%). Consider mode imputation or labeling as 'Unknown'."
        elif missing_pct < 20:
            severity = "moderate"
            if pd.api.types.is_numeric_dtype(series):
                rec = f"Moderate missingness ({missing_pct}%). Impute using median (for skewed data) or KNN/predictive imputation."
            else:
                rec = f"Moderate missingness ({missing_pct}%). Impute with most frequent category or evaluate missingness mechanism."
        elif missing_pct < 50:
            severity = "high"
            rec = f"High missingness ({missing_pct}%). Investigate data collection pipeline; consider an explicit missing indicator feature."
        else:
            severity = "critical"
            rec = f"Critical missingness ({missing_pct}%). Retaining this column may introduce bias; consider dropping it unless domain knowledge requires keeping it."

        by_column_details.append(
            MissingColumnDetail(
                column=str(col),
                missing_count=missing_count,
                missing_percentage=missing_pct,
                severity=severity,
                recommendation=rec
            )
        )

    overall_missing_pct = round((total_missing_cells / total_cells) * 100, 2)

    return MissingAnalysis(
        total_missing_cells=total_missing_cells,
        missing_cell_percentage=overall_missing_pct,
        columns_with_missing=columns_with_missing,
        by_column=by_column_details
    )
