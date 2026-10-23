# Explainable Data Quality Scoring Methodology

## Overview

Unlike opaque machine-learning models or arbitrary black-box scores, the **Smart Data Quality Analyzer** uses an explainable, deterministic heuristic index.

The index starts at a **baseline of 100 points** and subtracts penalties based on observed defect proportions.

$$\text{Final Score} = \max\left(0, \min\left(100, 100 - \sum \text{Penalties}\right)\right)$$

---

## Penalty Dimensions & Maximum Weights

| Defect Dimension | Maximum Penalty | Formula / Weighting Logic |
| :--- | :--- | :--- |
| **Missing Values** | **25 Points** | $\min\left(1.0, \frac{\text{Missing Cells}}{\text{Total Cells}}\right) \times 25.0$ |
| **Duplicate Records** | **20 Points** | $\min\left(1.0, \frac{\text{Duplicate Rows}}{\text{Total Rows}}\right) \times 20.0$ |
| **Numerical Outliers** | **15 Points** | $\min\left(1.0, \frac{\text{Outlier Values}}{\text{Total Numerical Cells}}\right) \times 15.0$ |
| **Type Inconsistencies**| **15 Points** | $\min\left(1.0, \frac{\text{Inconsistent Columns}}{\text{Total Columns}}\right) \times 15.0$ |
| **Constant / Low Variance**| **15 Points** | $\min\left(1.0, \frac{\text{Constant Columns}}{\text{Total Columns}}\right) \times 15.0$ |
| **Category Casing Issues**| **10 Points** | $\min\left(1.0, \frac{\text{Inconsistent Category Columns}}{\text{Total Columns}}\right) \times 10.0$ |

---

## Qualitative Grading Scale

- **90.0 – 100.0**: **Grade A (Excellent)** — Dataset is clean, complete, and ready for modeling.
- **80.0 – 89.9**: **Grade B (Good)** — Minor issues (e.g. low missingness or minor casing variations).
- **70.0 – 79.9**: **Grade C (Fair)** — Noticeable missing values or moderate outliers requiring imputation.
- **60.0 – 69.9**: **Grade D (Poor)** — High duplicate count or mixed data types; cleaning is required.
- **< 60.0**: **Grade F (Critical Quality Defects)** — Severe data quality problems; unsafe for reliable machine learning inference.

---

## Statistical Methods Employed

### 1. Tukey's Interquartile Range (IQR)
- $Q_1 = \text{25th percentile}$
- $Q_3 = \text{75th percentile}$
- $\text{IQR} = Q_3 - Q_1$
- $\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}$
- $\text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$

### 2. Standard Z-Score
$$z = \frac{x - \mu}{\sigma}$$
Flags observations where $|z| > 3.0$ standard deviations from the sample mean.

### 3. Isolation Forest (scikit-learn)
Applied to multi-dimensional numerical subsets ($d \ge 2$) to detect non-linear multi-variate anomalies that univariate IQR/Z-scores cannot detect.

---

## Disclaimer
> [!NOTE]
> This heuristic score is a project-defined diagnostic index for portfolio and dataset screening. It does not constitute an ISO data management certification or a guarantee that the underlying facts in the records are true.
