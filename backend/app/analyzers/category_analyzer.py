"""Category consistency and case variation analyzer."""

from collections import defaultdict
from typing import List
import pandas as pd
from app.schemas.models import CategoryInconsistency, CategoryVariantCluster


def analyze_category_consistency(df: pd.DataFrame) -> List[CategoryInconsistency]:
    """
    Scans categorical / string columns for casing differences and whitespace
    variations (e.g. 'Chennai', 'chennai', 'CHENNAI').
    Groups them into clusters for user review without modifying the data.
    """
    inconsistencies: List[CategoryInconsistency] = []

    for col in df.columns:
        series = df[col].dropna()
        # Only inspect non-numeric columns with manageable cardinality (e.g., <= 100 distinct values)
        if pd.api.types.is_numeric_dtype(series):
            continue

        raw_values = series.astype(str).tolist()
        unique_raw = set(raw_values)
        if len(unique_raw) < 2 or len(unique_raw) > 300:
            continue

        # Group by lowercase + stripped version
        canonical_map = defaultdict(lambda: defaultdict(int))
        for val in raw_values:
            cleaned = val.strip().lower()
            if cleaned:
                canonical_map[cleaned][val] += 1

        # Identify clusters with more than one distinct string representation
        clusters: List[CategoryVariantCluster] = []
        for canonical, variants_dict in canonical_map.items():
            if len(variants_dict) > 1:
                clusters.append(
                    CategoryVariantCluster(
                        canonical=canonical.title(),  # Recommended normalized label
                        variations=list(variants_dict.keys()),
                        frequency_breakdown=dict(variants_dict)
                    )
                )

        if clusters:
            total_variant_groups = len(clusters)
            rec = (
                f"Found {total_variant_groups} category groups with inconsistent casing/whitespace "
                "(e.g., capitalization discrepancies). Review and choose whether to normalize."
            )
            inconsistencies.append(
                CategoryInconsistency(
                    column=str(col),
                    unique_count=len(unique_raw),
                    clusters=clusters,
                    recommendation=rec
                )
            )

    return inconsistencies
