"""Constant and low-information (quasi-constant) column analyzer."""

from typing import List
import pandas as pd
from app.schemas.models import ConstantColumnDetail


def analyze_constant_columns(df: pd.DataFrame) -> List[ConstantColumnDetail]:
    """
    Detects constant columns (1 unique non-null value) and low-information
    columns (where a single value dominates >= 90% of all rows).
    """
    details: List[ConstantColumnDetail] = []
    total_rows = len(df)
    if total_rows == 0:
        return details

    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        unique_cnt = series.nunique()
        val_counts = series.value_counts()
        top_val = str(val_counts.index[0])
        top_freq = int(val_counts.iloc[0])
        top_pct = round((top_freq / total_rows) * 100, 2)

        if unique_cnt == 1:
            details.append(
                ConstantColumnDetail(
                    column=str(col),
                    unique_count=1,
                    top_value=top_val,
                    top_value_frequency=top_freq,
                    top_value_percentage=top_pct,
                    issue_type="constant",
                    explanation=(
                        f"Column has zero variance (100% '{top_val}'). "
                        "Constant columns provide zero predictive signal or analytical variation "
                        "and can usually be safely dropped."
                    )
                )
            )
        elif top_pct >= 90.0 and unique_cnt > 1:
            details.append(
                ConstantColumnDetail(
                    column=str(col),
                    unique_count=unique_cnt,
                    top_value=top_val,
                    top_value_frequency=top_freq,
                    top_value_percentage=top_pct,
                    issue_type="low_information",
                    explanation=(
                        f"Quasi-constant column: {top_pct}% of values are '{top_val}'. "
                        "Has very low information entropy and may not differentiate records effectively."
                    )
                )
            )

    return details
