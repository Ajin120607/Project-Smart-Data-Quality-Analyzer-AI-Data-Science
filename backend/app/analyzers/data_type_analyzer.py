"""Data type inference and type inconsistency analyzer."""

import re
from typing import Any, List
import pandas as pd
from app.schemas.models import DataTypeColumnDetail


def is_numeric_string(val: str) -> bool:
    """Checks if a string represents an integer or float value."""
    cleaned = val.strip().replace(",", "").replace("$", "").replace("€", "").replace("₹", "")
    try:
        float(cleaned)
        return True
    except ValueError:
        return False


def is_datetime_string(val: str) -> bool:
    """Checks if a string conforms to common date / datetime formats."""
    val_clean = val.strip()
    if len(val_clean) < 6 or len(val_clean) > 30:
        return False
    # Check common regex patterns for YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, etc.
    patterns = [
        r'^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}',
        r'^\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}',
    ]
    for pat in patterns:
        if re.match(pat, val_clean):
            return True
    return False


def analyze_data_types(df: pd.DataFrame) -> List[DataTypeColumnDetail]:
    """
    Infers data types, detects numeric and datetime values trapped as object/text,
    and identifies mixed data types within individual columns.
    """
    details: List[DataTypeColumnDetail] = []

    for col in df.columns:
        series = df[col].dropna()
        pandas_dtype = str(df[col].dtype)
        sample_values = [str(x) for x in series.head(5).tolist()]

        if len(series) == 0:
            details.append(
                DataTypeColumnDetail(
                    column=str(col),
                    inferred_type="empty",
                    pandas_dtype=pandas_dtype,
                    is_mixed=False,
                    numeric_as_text=False,
                    datetime_as_text=False,
                    sample_values=[],
                    suggestion="Column has no non-null records to evaluate."
                )
            )
            continue

        # If already numerical
        if pd.api.types.is_integer_dtype(df[col]):
            details.append(
                DataTypeColumnDetail(
                    column=str(col),
                    inferred_type="integer",
                    pandas_dtype=pandas_dtype,
                    is_mixed=False,
                    numeric_as_text=False,
                    datetime_as_text=False,
                    sample_values=sample_values,
                    suggestion=None
                )
            )
            continue

        if pd.api.types.is_float_dtype(df[col]):
            details.append(
                DataTypeColumnDetail(
                    column=str(col),
                    inferred_type="float",
                    pandas_dtype=pandas_dtype,
                    is_mixed=False,
                    numeric_as_text=False,
                    datetime_as_text=False,
                    sample_values=sample_values,
                    suggestion=None
                )
            )
            continue

        # If object or string type, inspect entries
        str_series = series.astype(str).str.strip()
        num_numeric = sum(1 for v in str_series if is_numeric_string(v))
        num_datetime = sum(1 for v in str_series if is_datetime_string(v))
        num_total = len(str_series)

        numeric_ratio = num_numeric / num_total
        datetime_ratio = num_datetime / num_total

        is_mixed = False
        numeric_as_text = False
        datetime_as_text = False
        inferred = "string"
        suggestion = None

        if numeric_ratio >= 0.90:
            inferred = "numeric (stored as text)"
            numeric_as_text = True
            suggestion = "Consider converting this text column to integer or float for mathematical operations."
        elif datetime_ratio >= 0.75:
            inferred = "datetime (stored as text)"
            datetime_as_text = True
            suggestion = "Consider parsing this text column as datetime for chronological and time-series analysis."
        elif 0.10 <= numeric_ratio < 0.90:
            is_mixed = True
            inferred = "mixed (numbers and text)"
            suggestion = f"Column contains mixed content ({round(numeric_ratio * 100, 1)}% numeric values alongside text). Verify and clean."
        elif 0.10 <= datetime_ratio < 0.75:
            is_mixed = True
            inferred = "mixed (dates and text)"
            suggestion = "Column appears to contain mixed date and text formats. Standardize format."

        details.append(
            DataTypeColumnDetail(
                column=str(col),
                inferred_type=inferred,
                pandas_dtype=pandas_dtype,
                is_mixed=is_mixed,
                numeric_as_text=numeric_as_text,
                datetime_as_text=datetime_as_text,
                sample_values=sample_values,
                suggestion=suggestion
            )
        )

    return details
