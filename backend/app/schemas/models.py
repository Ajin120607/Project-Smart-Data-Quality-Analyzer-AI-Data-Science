"""Pydantic schemas for data quality analysis and cleaning requests and responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    file_name: str
    file_size_kb: float
    total_rows: int
    total_columns: int
    column_names: List[str]
    memory_usage_kb: float


class QualityScoreBreakdown(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    grade: str
    penalties: Dict[str, float]
    max_penalties: Dict[str, float]
    formula_explanation: str
    disclaimer: str


class MissingColumnDetail(BaseModel):
    column: str
    missing_count: int
    missing_percentage: float
    severity: str
    recommendation: str


class MissingAnalysis(BaseModel):
    total_missing_cells: int
    missing_cell_percentage: float
    columns_with_missing: int
    by_column: List[MissingColumnDetail]


class DuplicateAnalysis(BaseModel):
    duplicate_row_count: int
    duplicate_percentage: float
    total_rows: int
    unique_rows: int
    sample_duplicates: List[Dict[str, Any]]


class OutlierColumnDetail(BaseModel):
    column: str
    method: str
    outlier_count: int
    outlier_percentage: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    sample_outliers: List[Any] = []
    recommendation: str


class OutlierAnalysis(BaseModel):
    total_outliers: int
    columns_affected: int
    method: str
    by_column: List[OutlierColumnDetail]
    ml_anomaly_detection: Optional[Dict[str, Any]] = None


class DataTypeColumnDetail(BaseModel):
    column: str
    inferred_type: str
    pandas_dtype: str
    is_mixed: bool
    numeric_as_text: bool
    datetime_as_text: bool
    sample_values: List[Any]
    suggestion: Optional[str] = None


class CategoryVariantCluster(BaseModel):
    canonical: str
    variations: List[str]
    frequency_breakdown: Dict[str, int]


class CategoryInconsistency(BaseModel):
    column: str
    unique_count: int
    clusters: List[CategoryVariantCluster]
    recommendation: str


class ConstantColumnDetail(BaseModel):
    column: str
    unique_count: int
    top_value: Optional[str] = None
    top_value_frequency: int
    top_value_percentage: float
    issue_type: str  # 'constant' | 'low_information'
    explanation: str


class RecommendationItem(BaseModel):
    category: str
    severity: str  # 'critical' | 'warning' | 'info'
    title: str
    description: str
    suggested_action: str


class QualityReport(BaseModel):
    report_id: str
    session_id: str
    generated_at: str
    summary: DatasetSummary
    quality_score: QualityScoreBreakdown
    missing: MissingAnalysis
    duplicates: DuplicateAnalysis
    outliers: OutlierAnalysis
    data_types: List[DataTypeColumnDetail]
    category_consistency: List[CategoryInconsistency]
    constant_and_low_variance: List[ConstantColumnDetail]
    statistics: Dict[str, Dict[str, Any]]
    recommendations: List[RecommendationItem]
    preview_rows: List[Dict[str, Any]]


class CleanRequest(BaseModel):
    session_id: Optional[str] = None
    report_id: Optional[str] = None
    selected_columns: Optional[List[str]] = None
    remove_duplicates: bool = False
    drop_columns: Optional[List[str]] = None
    handle_missing_num: Optional[str] = None  # 'mean', 'median', 'mode', 'drop_row', None
    handle_missing_cat: Optional[str] = None  # 'mode', 'placeholder', 'drop_row', None
    missing_cat_placeholder: str = "Unknown"
    normalize_categories: bool = False
    handle_outliers: Optional[str] = None  # 'clip_iqr', 'remove_rows', None
    outlier_method: str = "iqr"


class CleanOperationLog(BaseModel):
    operation: str
    affected_elements: int
    details: str


class CleanResponse(BaseModel):
    file_id: str
    original_rows: int
    cleaned_rows: int
    original_cols: int
    cleaned_cols: int
    operations_applied: List[CleanOperationLog]
    preview_rows: List[Dict[str, Any]]
    comparison: Dict[str, Any]
