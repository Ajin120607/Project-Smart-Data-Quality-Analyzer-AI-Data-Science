"""Outlier detection engine using IQR, Z-Score, and optional Isolation Forest."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

# Gracefully handle optional scikit-learn for lightweight serverless environments (like Vercel)
try:
    from sklearn.ensemble import IsolationForest
    HAS_SKLEARN = True
except (ImportError, ModuleNotFoundError):
    HAS_SKLEARN = False

from app.schemas.models import OutlierAnalysis, OutlierColumnDetail


def detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """Calculates outliers using the Tukey Interquartile Range (IQR) method."""
    clean_series = series.dropna()
    if len(clean_series) < 4:
        return {
            "count": 0,
            "indices": [],
            "lower_bound": None,
            "upper_bound": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "samples": []
        }

    q1 = float(clean_series.quantile(0.25))
    q3 = float(clean_series.quantile(0.75))
    iqr = float(q3 - q1)

    lower_bound = float(q1 - 1.5 * iqr)
    upper_bound = float(q3 + 1.5 * iqr)

    outlier_mask = (clean_series < lower_bound) | (clean_series > upper_bound)
    outlier_values = clean_series[outlier_mask]

    return {
        "count": int(outlier_mask.sum()),
        "indices": outlier_values.index.tolist(),
        "lower_bound": round(lower_bound, 4),
        "upper_bound": round(upper_bound, 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "samples": [round(float(v), 4) for v in outlier_values.head(10).tolist()]
    }


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> Dict[str, Any]:
    """Calculates outliers using standard Z-score (|z| > threshold)."""
    clean_series = series.dropna()
    if len(clean_series) < 4 or clean_series.std() == 0:
        return {
            "count": 0,
            "indices": [],
            "mean": None,
            "std": None,
            "samples": []
        }

    mean = float(clean_series.mean())
    std = float(clean_series.std())

    z_scores = np.abs((clean_series - mean) / std)
    outlier_mask = z_scores > threshold
    outlier_values = clean_series[outlier_mask]

    return {
        "count": int(outlier_mask.sum()),
        "indices": outlier_values.index.tolist(),
        "mean": round(mean, 4),
        "std": round(std, 4),
        "samples": [round(float(v), 4) for v in outlier_values.head(10).tolist()]
    }


def run_isolation_forest_anomaly(df_numeric: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Runs multi-dimensional anomaly detection using scikit-learn IsolationForest
    when at least 2 numerical columns and >= 10 rows are available.
    """
    if not HAS_SKLEARN:
        return None

    if df_numeric.shape[1] < 2 or len(df_numeric) < 10:
        return None

    try:
        filled = df_numeric.fillna(df_numeric.median())
        iso = IsolationForest(
            contamination="auto",
            random_state=42,
            n_estimators=100
        )
        preds = iso.fit_predict(filled)
        anomaly_count = int((preds == -1).sum())
        anomaly_pct = round((anomaly_count / len(df_numeric)) * 100, 2)

        return {
            "method": "Isolation Forest (scikit-learn)",
            "anomalous_rows_detected": anomaly_count,
            "anomalous_percentage": anomaly_pct,
            "features_analyzed": df_numeric.columns.tolist(),
            "explanation": (
                "Isolation Forest isolates anomalies by randomly partitioning feature space. "
                "Data points requiring fewer partitions are flagged as multi-variate anomalies."
            )
        }
    except Exception:
        return None


def analyze_outliers(df: pd.DataFrame, method: str = "iqr") -> OutlierAnalysis:
    """
    Analyzes numerical columns for outliers using either the IQR or Z-score method,
    supplemented with an explainable multi-feature Isolation Forest check.
    """
    by_column: List[OutlierColumnDetail] = []
    total_outliers = 0
    columns_affected = 0

    # Extract numerical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        series = df[col]
        total_valid = len(series.dropna())
        if total_valid == 0:
            continue

        if method == "zscore":
            res = detect_outliers_zscore(series)
            cnt = res["count"]
            pct = round((cnt / total_valid) * 100, 2) if total_valid > 0 else 0.0
            rec = (
                f"Z-score method flagged {cnt} values (|z| > 3.0). "
                "Remember that outliers reflect extreme statistical deviation, not necessarily recording errors."
            )
            col_detail = OutlierColumnDetail(
                column=str(col),
                method="Z-Score (|z| > 3)",
                outlier_count=cnt,
                outlier_percentage=pct,
                mean=res.get("mean"),
                std=res.get("std"),
                sample_outliers=res.get("samples", []),
                recommendation=rec
            )
        else:
            res = detect_outliers_iqr(series)
            cnt = res["count"]
            pct = round((cnt / total_valid) * 100, 2) if total_valid > 0 else 0.0
            rec = (
                f"IQR method flagged {cnt} values outside [{res.get('lower_bound')}, {res.get('upper_bound')}]. "
                "Inspect these records in context before deciding to truncate, transform, or retain them."
            )
            col_detail = OutlierColumnDetail(
                column=str(col),
                method="IQR (Tukey 1.5x)",
                outlier_count=cnt,
                outlier_percentage=pct,
                lower_bound=res.get("lower_bound"),
                upper_bound=res.get("upper_bound"),
                q1=res.get("q1"),
                q3=res.get("q3"),
                iqr=res.get("iqr"),
                sample_outliers=res.get("samples", []),
                recommendation=rec
            )

        total_outliers += cnt
        if cnt > 0:
            columns_affected += 1
        by_column.append(col_detail)

    # Optional ML Isolation Forest
    ml_result = None
    if len(numeric_cols) >= 2 and HAS_SKLEARN:
        ml_result = run_isolation_forest_anomaly(df[numeric_cols])

    return OutlierAnalysis(
        total_outliers=total_outliers,
        columns_affected=columns_affected,
        method=method,
        by_column=by_column,
        ml_anomaly_detection=ml_result
    )
