"""Transparent, explainable heuristic data quality scoring engine."""

from typing import Dict, List
import pandas as pd
from app.schemas.models import (
    CategoryInconsistency,
    ConstantColumnDetail,
    DataTypeColumnDetail,
    DuplicateAnalysis,
    MissingAnalysis,
    OutlierAnalysis,
    QualityScoreBreakdown,
)

MAX_PENALTIES = {
    "missing_values": 25.0,
    "duplicate_records": 20.0,
    "outliers": 15.0,
    "type_inconsistencies": 15.0,
    "constant_columns": 15.0,
    "category_inconsistencies": 10.0,
}


def calculate_quality_score(
    df: pd.DataFrame,
    missing: MissingAnalysis,
    duplicates: DuplicateAnalysis,
    outliers: OutlierAnalysis,
    data_types: List[DataTypeColumnDetail],
    categories: List[CategoryInconsistency],
    constants: List[ConstantColumnDetail]
) -> QualityScoreBreakdown:
    """
    Computes an explainable, bounded score (0 to 100) starting at 100
    with explicit penalties for dataset hygiene defects.
    """
    penalties: Dict[str, float] = {}

    # 1. Missing Values penalty (Max 25 pts)
    # Penalty scaled by missing cell percentage
    # E.g. 10% missing cells = 0.10 * 25 = 2.5 pts; 100% missing = 25 pts.
    missing_ratio = min(1.0, missing.missing_cell_percentage / 100.0)
    penalties["missing_values"] = round(missing_ratio * MAX_PENALTIES["missing_values"], 2)

    # 2. Duplicate Records penalty (Max 20 pts)
    # Scaled by duplicate row percentage
    dup_ratio = min(1.0, duplicates.duplicate_percentage / 100.0)
    penalties["duplicate_records"] = round(dup_ratio * MAX_PENALTIES["duplicate_records"], 2)

    # 3. Outlier penalty (Max 15 pts)
    # Scaled by percentage of numerical cells flagged as outliers
    numeric_cells = 0
    for col_det in outliers.by_column:
        # approximate valid rows for that col
        numeric_cells += len(df)
    
    if numeric_cells > 0:
        outlier_ratio = min(1.0, outliers.total_outliers / numeric_cells)
    else:
        outlier_ratio = 0.0
    penalties["outliers"] = round(outlier_ratio * MAX_PENALTIES["outliers"], 2)

    # 4. Type Inconsistencies penalty (Max 15 pts)
    # Points deducted per column with mixed types or numeric/date stored as text
    total_cols = max(1, len(df.columns))
    inconsistent_type_cols = sum(
        1 for dt in data_types if dt.is_mixed or dt.numeric_as_text or dt.datetime_as_text
    )
    type_ratio = min(1.0, inconsistent_type_cols / total_cols)
    penalties["type_inconsistencies"] = round(type_ratio * MAX_PENALTIES["type_inconsistencies"], 2)

    # 5. Constant & Low Variance columns penalty (Max 15 pts)
    constant_cols = len(constants)
    const_ratio = min(1.0, constant_cols / total_cols)
    penalties["constant_columns"] = round(const_ratio * MAX_PENALTIES["constant_columns"], 2)

    # 6. Category Inconsistencies penalty (Max 10 pts)
    cat_inconsistencies_cnt = len(categories)
    cat_ratio = min(1.0, cat_inconsistencies_cnt / total_cols)
    penalties["category_inconsistencies"] = round(cat_ratio * MAX_PENALTIES["category_inconsistencies"], 2)

    # Compute total penalty and clamp score between 0 and 100
    total_penalty = sum(penalties.values())
    raw_score = 100.0 - total_penalty
    overall_score = round(max(0.0, min(100.0, raw_score)), 1)

    # Grade determination
    if overall_score >= 90:
        grade = "A (Excellent)"
    elif overall_score >= 80:
        grade = "B (Good)"
    elif overall_score >= 70:
        grade = "C (Fair)"
    elif overall_score >= 60:
        grade = "D (Poor)"
    else:
        grade = "F (Critical Quality Defects)"

    formula = (
        "Score = 100 - [Missing Penalty (max 25) + Duplicates Penalty (max 20) + "
        "Outliers Penalty (max 15) + Type Inconsistency Penalty (max 15) + "
        "Constant Columns Penalty (max 15) + Category Penalty (max 10)]"
    )

    disclaimer = (
        "Note: This score is an explainable project-defined heuristic index designed for "
        "data hygiene assessment in portfolio workflows. It does not constitute an "
        "industry-standard metric, ground-truth verification, or guarantee of factual accuracy."
    )

    return QualityScoreBreakdown(
        overall_score=overall_score,
        grade=grade,
        penalties=penalties,
        max_penalties=MAX_PENALTIES,
        formula_explanation=formula,
        disclaimer=disclaimer
    )
