"""Central analysis engine orchestrating quality checks and recommendations."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import math
import numpy as np
import pandas as pd

from app.schemas.models import (
    DatasetSummary,
    QualityReport,
    RecommendationItem,
)
from app.analyzers.missing_analyzer import analyze_missing_values
from app.analyzers.duplicate_analyzer import analyze_duplicates
from app.analyzers.outlier_analyzer import analyze_outliers
from app.analyzers.data_type_analyzer import analyze_data_types
from app.analyzers.category_analyzer import analyze_category_consistency
from app.analyzers.column_analyzer import analyze_constant_columns
from app.analyzers.quality_scorer import calculate_quality_score
from app.utils.security import generate_secure_id


def sanitize_for_json(obj: Any) -> Any:
    """Recursively converts NaN, Infinity, and numpy datatypes to JSON-compliant primitives."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (np.floating, np.integer)):
        val = obj.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return val
    elif isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif pd.isna(obj):
        return None
    return obj


def generate_recommendations(
    missing_analysis,
    duplicate_analysis,
    outlier_analysis,
    data_types,
    category_inconsistencies,
    constant_columns
) -> List[RecommendationItem]:
    """Generates dynamic, actionable recommendations tailored to observed defects."""
    recs: List[RecommendationItem] = []

    # 1. Missing values recommendations
    if missing_analysis.columns_with_missing > 0:
        high_missing_cols = [
            c for c in missing_analysis.by_column if c.missing_percentage >= 20.0
        ]
        moderate_missing_cols = [
            c for c in missing_analysis.by_column if 5.0 <= c.missing_percentage < 20.0
        ]

        if high_missing_cols:
            col_names = ", ".join([f"'{c.column}' ({c.missing_percentage}%)" for c in high_missing_cols])
            recs.append(
                RecommendationItem(
                    category="Missing Values",
                    severity="critical" if any(c.missing_percentage >= 50 for c in high_missing_cols) else "warning",
                    title="High missingness in specific columns",
                    description=f"Columns {col_names} exhibit high missing percentages.",
                    suggested_action="Review data collection pipeline. Consider dropping columns with >50% missing data if non-essential."
                )
            )

        if moderate_missing_cols:
            col_names = ", ".join([f"'{c.column}'" for c in moderate_missing_cols])
            recs.append(
                RecommendationItem(
                    category="Missing Values",
                    severity="warning",
                    title="Moderate missing values requiring imputation",
                    description=f"Columns {col_names} contain 5% to 20% missing values.",
                    suggested_action="Apply median imputation for skewed numerical features or mode imputation for categorical attributes."
                )
            )

    # 2. Duplicate recommendations
    if duplicate_analysis.duplicate_row_count > 0:
        recs.append(
            RecommendationItem(
                category="Duplicates",
                severity="warning" if duplicate_analysis.duplicate_percentage > 5.0 else "info",
                title=f"Detected {duplicate_analysis.duplicate_row_count} duplicate row(s)",
                description=f"{duplicate_analysis.duplicate_percentage}% of dataset rows are exact duplicates.",
                suggested_action="Inspect the sample duplicate records. Use the interactive cleaning tool to deduplicate."
            )
        )

    # 3. Outlier recommendations
    if outlier_analysis.total_outliers > 0:
        top_outlier_cols = [c for c in outlier_analysis.by_column if c.outlier_count > 0]
        col_summary = ", ".join([f"'{c.column}' ({c.outlier_count} outliers)" for c in top_outlier_cols[:3]])
        recs.append(
            RecommendationItem(
                category="Outliers",
                severity="info",
                title=f"Extreme values flagged in {outlier_analysis.columns_affected} numerical column(s)",
                description=f"Outliers detected in {col_summary}. Outliers are unusual observations, not necessarily errors.",
                suggested_action="Inspect the records to verify whether they represent valid real-world extremes or data entry anomalies."
            )
        )

    # 4. Data types recommendations
    text_nums = [dt for dt in data_types if dt.numeric_as_text]
    mixed_types = [dt for dt in data_types if dt.is_mixed]
    text_dates = [dt for dt in data_types if dt.datetime_as_text]

    if text_nums:
        names = ", ".join([f"'{dt.column}'" for dt in text_nums])
        recs.append(
            RecommendationItem(
                category="Data Types",
                severity="warning",
                title="Numeric values stored as text strings",
                description=f"Columns {names} contain numbers formatted as text.",
                suggested_action="Convert these columns to float/integer to enable mathematical calculations and statistical modeling."
            )
        )

    if mixed_types:
        names = ", ".join([f"'{dt.column}'" for dt in mixed_types])
        recs.append(
            RecommendationItem(
                category="Data Types",
                severity="warning",
                title="Mixed data formats detected",
                description=f"Columns {names} contain a mix of numbers, dates, and arbitrary text.",
                suggested_action="Standardize column format by parsing and isolating non-conforming entries."
            )
        )

    if text_dates:
        names = ", ".join([f"'{dt.column}'" for dt in text_dates])
        recs.append(
            RecommendationItem(
                category="Data Types",
                severity="info",
                title="Date strings detected",
                description=f"Columns {names} look like timestamps but are stored as plain strings.",
                suggested_action="Parse to standard ISO-8601 (YYYY-MM-DD) datetime format for chronological indexing."
            )
        )

    # 5. Category inconsistencies
    if category_inconsistencies:
        names = ", ".join([f"'{ci.column}'" for ci in category_inconsistencies])
        recs.append(
            RecommendationItem(
                category="Categories",
                severity="info",
                title="Inconsistent capitalization/spacing in categories",
                description=f"Discrepancies like 'Chennai' vs 'chennai' found in {names}.",
                suggested_action="Normalize categories to Title Case using the cleaning tool to prevent duplicate cardinality."
            )
        )

    # 6. Constant / low information columns
    if constant_columns:
        constants = [c for c in constant_columns if c.issue_type == "constant"]
        low_info = [c for c in constant_columns if c.issue_type == "low_information"]

        if constants:
            names = ", ".join([f"'{c.column}'" for c in constants])
            recs.append(
                RecommendationItem(
                    category="Feature Variance",
                    severity="warning",
                    title="Zero-variance constant column(s)",
                    description=f"Columns {names} contain exactly one single value across all rows.",
                    suggested_action="Drop constant columns to reduce noise and simplify data storage."
                )
            )
        if low_info:
            names = ", ".join([f"'{c.column}' ({c.top_value_percentage}%)" for c in low_info])
            recs.append(
                RecommendationItem(
                    category="Feature Variance",
                    severity="info",
                    title="Quasi-constant columns with low entropy",
                    description=f"Columns {names} have >=90% identical values.",
                    suggested_action="Assess whether these columns provide sufficient analytical variation for modeling."
                )
            )

    if not recs:
        recs.append(
            RecommendationItem(
                category="General",
                severity="info",
                title="Clean and well-structured dataset",
                description="No significant data hygiene defects were detected across evaluated dimensions.",
                suggested_action="Dataset is ready for exploratory data analysis (EDA) and downstream modeling."
            )
        )

    return recs


def compute_statistics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Calculates statistical summaries for numerical and categorical attributes."""
    stats: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        series = df[col]
        col_type = "numeric" if pd.api.types.is_numeric_dtype(series) else "categorical"

        if col_type == "numeric":
            valid = series.dropna()
            if len(valid) > 0:
                stats[str(col)] = {
                    "type": "numeric",
                    "count": int(valid.count()),
                    "mean": round(float(valid.mean()), 2) if not math.isnan(valid.mean()) else None,
                    "std": round(float(valid.std()), 2) if len(valid) > 1 and not math.isnan(valid.std()) else 0.0,
                    "min": round(float(valid.min()), 2) if not math.isnan(valid.min()) else None,
                    "q25": round(float(valid.quantile(0.25)), 2) if not math.isnan(valid.quantile(0.25)) else None,
                    "median": round(float(valid.median()), 2) if not math.isnan(valid.median()) else None,
                    "q75": round(float(valid.quantile(0.75)), 2) if not math.isnan(valid.quantile(0.75)) else None,
                    "max": round(float(valid.max()), 2) if not math.isnan(valid.max()) else None,
                    "skewness": round(float(valid.skew()), 2) if len(valid) > 2 and not math.isnan(valid.skew()) else 0.0,
                }
            else:
                stats[str(col)] = {"type": "numeric", "count": 0}
        else:
            valid = series.dropna().astype(str)
            if len(valid) > 0:
                top_val = valid.mode().iloc[0] if len(valid.mode()) > 0 else "N/A"
                freq = int((valid == top_val).sum())
                stats[str(col)] = {
                    "type": "categorical",
                    "count": int(valid.count()),
                    "unique": int(valid.nunique()),
                    "top": top_val,
                    "freq": freq,
                }
            else:
                stats[str(col)] = {"type": "categorical", "count": 0, "unique": 0}

    return sanitize_for_json(stats)


def generate_quality_report(
    df: pd.DataFrame,
    file_name: str,
    file_size_kb: float,
    session_id: str,
    outlier_method: str = "iqr",
    selected_columns: Optional[List[str]] = None
) -> QualityReport:
    """Runs all data quality analyzers and assembles the comprehensive report."""
    # Filter columns if selected
    working_df = df[selected_columns] if selected_columns else df

    # Run analyzers
    missing_analysis = analyze_missing_values(working_df)
    duplicate_analysis = analyze_duplicates(working_df)
    outlier_analysis = analyze_outliers(working_df, method=outlier_method)
    data_types = analyze_data_types(working_df)
    category_inconsistencies = analyze_category_consistency(working_df)
    constant_columns = analyze_constant_columns(working_df)

    # Compute heuristic quality score
    quality_score = calculate_quality_score(
        df=working_df,
        missing=missing_analysis,
        duplicates=duplicate_analysis,
        outliers=outlier_analysis,
        data_types=data_types,
        categories=category_inconsistencies,
        constants=constant_columns
    )

    # Compute descriptive statistics
    stats = compute_statistics(working_df)

    # Generate actionable recommendations
    recommendations = generate_recommendations(
        missing_analysis=missing_analysis,
        duplicate_analysis=duplicate_analysis,
        outlier_analysis=outlier_analysis,
        data_types=data_types,
        category_inconsistencies=category_inconsistencies,
        constant_columns=constant_columns
    )

    # Preview rows (first 10 rows converted safely to JSON dicts)
    raw_preview = working_df.head(10).to_dict(orient="records")
    preview_rows = sanitize_for_json(raw_preview)

    report_id = generate_secure_id()
    mem_kb = round(working_df.memory_usage(deep=True).sum() / 1024, 2)

    summary = DatasetSummary(
        file_name=file_name,
        file_size_kb=file_size_kb,
        total_rows=len(working_df),
        total_columns=len(working_df.columns),
        column_names=[str(c) for c in working_df.columns],
        memory_usage_kb=mem_kb
    )

    return QualityReport(
        report_id=report_id,
        session_id=session_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        summary=summary,
        quality_score=quality_score,
        missing=missing_analysis,
        duplicates=duplicate_analysis,
        outliers=outlier_analysis,
        data_types=data_types,
        category_consistency=category_inconsistencies,
        constant_and_low_variance=constant_columns,
        statistics=stats,
        recommendations=recommendations,
        preview_rows=preview_rows
    )
