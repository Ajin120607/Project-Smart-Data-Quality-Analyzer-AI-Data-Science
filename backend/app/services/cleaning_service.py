"""Interactive cleaning engine applying explicitly selected data cleansing operations."""

import io
import math
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from app.schemas.models import CleanOperationLog, CleanRequest, CleanResponse
from app.analyzers.missing_analyzer import PLACEHOLDER_MISSING_STRINGS
from app.analyzers.outlier_analyzer import detect_outliers_iqr
from app.services.session_store import session_store


def sanitize_dict_list(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts NaNs and Infs to None for JSON safety."""
    cleaned = []
    for row in records:
        cleaned_row = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                cleaned_row[k] = None
            elif pd.isna(v):
                cleaned_row[k] = None
            else:
                cleaned_row[k] = v
        cleaned.append(cleaned_row)
    return cleaned


def clean_dataset(
    original_df: pd.DataFrame,
    clean_req: CleanRequest,
    file_name: str
) -> Tuple[pd.DataFrame, CleanResponse, bytes]:
    """
    Applies user-selected cleaning operations on an isolated copy of the dataset.
    Returns the cleaned DataFrame, the API response object, and raw CSV bytes.
    """
    df = original_df.copy()
    initial_rows = len(df)
    initial_cols = len(df.columns)
    operations: List[CleanOperationLog] = []

    # 1. Filter / Select Columns if specified
    if clean_req.selected_columns:
        valid_cols = [c for c in clean_req.selected_columns if c in df.columns]
        if valid_cols:
            dropped_count = len(df.columns) - len(valid_cols)
            df = df[valid_cols]
            if dropped_count > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Select Columns",
                        affected_elements=dropped_count,
                        details=f"Retained {len(valid_cols)} selected columns; excluded {dropped_count} columns."
                    )
                )

    # 2. Explicitly Drop Columns
    if clean_req.drop_columns:
        cols_to_drop = [c for c in clean_req.drop_columns if c in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            operations.append(
                CleanOperationLog(
                    operation="Drop Columns",
                    affected_elements=len(cols_to_drop),
                    details=f"Dropped columns: {', '.join(cols_to_drop)}"
                )
            )

    # 3. Deduplicate
    if clean_req.remove_duplicates:
        dups_count = int(df.duplicated().sum())
        if dups_count > 0:
            df = df.drop_duplicates(keep="first")
            operations.append(
                CleanOperationLog(
                    operation="Remove Duplicates",
                    affected_elements=dups_count,
                    details=f"Removed {dups_count} identical duplicate row(s)."
                )
            )

    # 4. Normalize Categories (Case standardization & whitespace stripping)
    if clean_req.normalize_categories:
        modified_cols = 0
        for col in df.columns:
            if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
                original_series = df[col].copy()
                # Strip and Title Case valid strings
                df[col] = df[col].apply(
                    lambda x: str(x).strip().title() if pd.notna(x) and str(x).strip().lower() not in PLACEHOLDER_MISSING_STRINGS else x
                )
                if not original_series.equals(df[col]):
                    modified_cols += 1

        if modified_cols > 0:
            operations.append(
                CleanOperationLog(
                    operation="Normalize Categories",
                    affected_elements=modified_cols,
                    details=f"Standardized casing and stripped whitespace across {modified_cols} text column(s)."
                )
            )

    # 5. Handle Missing Numerical Values
    if clean_req.handle_missing_num:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        strategy = clean_req.handle_missing_num.lower()

        if strategy == "drop_row" and num_cols:
            before_cnt = len(df)
            df = df.dropna(subset=num_cols)
            dropped = before_cnt - len(df)
            if dropped > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Drop Missing Rows (Numerical)",
                        affected_elements=dropped,
                        details=f"Dropped {dropped} row(s) containing missing numerical values."
                    )
                )
        elif strategy in ["mean", "median", "mode"]:
            imputed_cells = 0
            for col in num_cols:
                null_mask = df[col].isna()
                missing_cnt = int(null_mask.sum())
                if missing_cnt > 0:
                    if strategy == "mean":
                        fill_val = df[col].mean()
                    elif strategy == "median":
                        fill_val = df[col].median()
                    else:  # mode
                        mode_s = df[col].mode()
                        fill_val = mode_s.iloc[0] if len(mode_s) > 0 else 0

                    df[col] = df[col].fillna(fill_val)
                    imputed_cells += missing_cnt

            if imputed_cells > 0:
                operations.append(
                    CleanOperationLog(
                        operation=f"Impute Missing Numerical ({strategy.title()})",
                        affected_elements=imputed_cells,
                        details=f"Imputed {imputed_cells} missing numerical cell(s) with column {strategy}."
                    )
                )

    # 6. Handle Missing Categorical Values
    if clean_req.handle_missing_cat:
        cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        strategy = clean_req.handle_missing_cat.lower()

        # First unify string placeholders to actual np.nan
        for col in cat_cols:
            df[col] = df[col].apply(
                lambda x: np.nan if str(x).strip().lower() in PLACEHOLDER_MISSING_STRINGS else x
            )

        if strategy == "drop_row" and cat_cols:
            before_cnt = len(df)
            df = df.dropna(subset=cat_cols)
            dropped = before_cnt - len(df)
            if dropped > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Drop Missing Rows (Categorical)",
                        affected_elements=dropped,
                        details=f"Dropped {dropped} row(s) with missing categorical values."
                    )
                )
        elif strategy == "mode":
            imputed_cells = 0
            for col in cat_cols:
                null_mask = df[col].isna()
                missing_cnt = int(null_mask.sum())
                if missing_cnt > 0:
                    mode_s = df[col].mode()
                    fill_val = mode_s.iloc[0] if len(mode_s) > 0 else "Unknown"
                    df[col] = df[col].fillna(fill_val)
                    imputed_cells += missing_cnt
            if imputed_cells > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Impute Categorical (Mode)",
                        affected_elements=imputed_cells,
                        details=f"Imputed {imputed_cells} cell(s) using most frequent category."
                    )
                )
        elif strategy == "placeholder":
            placeholder = clean_req.missing_cat_placeholder or "Unknown"
            imputed_cells = 0
            for col in cat_cols:
                null_mask = df[col].isna()
                missing_cnt = int(null_mask.sum())
                if missing_cnt > 0:
                    df[col] = df[col].fillna(placeholder)
                    imputed_cells += missing_cnt
            if imputed_cells > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Impute Categorical (Placeholder)",
                        affected_elements=imputed_cells,
                        details=f"Filled {imputed_cells} missing text cell(s) with '{placeholder}'."
                    )
                )

    # 7. Handle Outliers
    if clean_req.handle_outliers:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        strategy = clean_req.handle_outliers.lower()

        if strategy == "clip_iqr":
            clipped_count = 0
            for col in num_cols:
                res = detect_outliers_iqr(df[col])
                lb, ub = res.get("lower_bound"), res.get("upper_bound")
                if lb is not None and ub is not None and res["count"] > 0:
                    before_col = df[col].copy()
                    df[col] = df[col].clip(lower=lb, upper=ub)
                    clipped_count += int((before_col != df[col]).sum())

            if clipped_count > 0:
                operations.append(
                    CleanOperationLog(
                        operation="Cap Outliers (IQR Winsorization)",
                        affected_elements=clipped_count,
                        details=f"Capped {clipped_count} outlier value(s) to IQR bounds."
                    )
                )
        elif strategy == "remove_rows":
            rows_to_remove = set()
            for col in num_cols:
                res = detect_outliers_iqr(df[col])
                rows_to_remove.update(res["indices"])

            if rows_to_remove:
                df = df.drop(index=list(rows_to_remove), errors="ignore")
                operations.append(
                    CleanOperationLog(
                        operation="Remove Outlier Rows",
                        affected_elements=len(rows_to_remove),
                        details=f"Filtered out {len(rows_to_remove)} row(s) containing statistical outliers."
                    )
                )

    # Generate CSV bytes
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    # Store download artifact
    cleaned_filename = f"cleaned_{file_name}"
    file_id = session_store.store_download(csv_bytes, cleaned_filename)

    # Generate quick before/after comparison
    orig_missing = int(original_df.isna().sum().sum())
    clean_missing = int(df.isna().sum().sum())
    orig_dups = int(original_df.duplicated().sum())
    clean_dups = int(df.duplicated().sum())

    comparison = {
        "rows": {"before": initial_rows, "after": len(df), "diff": len(df) - initial_rows},
        "columns": {"before": initial_cols, "after": len(df.columns), "diff": len(df.columns) - initial_cols},
        "missing_cells": {"before": orig_missing, "after": clean_missing, "diff": clean_missing - orig_missing},
        "duplicate_rows": {"before": orig_dups, "after": clean_dups, "diff": clean_dups - orig_dups},
    }

    # Safe preview rows
    raw_preview = df.head(10).to_dict(orient="records")
    preview_records = sanitize_dict_list(raw_preview)

    response = CleanResponse(
        file_id=file_id,
        original_rows=initial_rows,
        cleaned_rows=len(df),
        original_cols=initial_cols,
        cleaned_cols=len(df.columns),
        operations_applied=operations,
        preview_rows=preview_records,
        comparison=comparison
    )

    return df, response, csv_bytes
