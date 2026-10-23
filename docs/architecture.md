# System Architecture & Technical Specifications

**Smart Data Quality Analyzer** is an explainable data hygiene and cleansing platform built using a modern decoupled client-server architecture.

```
+-------------------------------------------------------------------------+
|                              REACT FRONTEND                             |
|  (Vite + React 18 + JavaScript + Recharts + Lucide Icons + CSS Variables)|
+-------------------------------------------------------------------------+
                                    │
                                    │ HTTP / JSON & Multipart (Fetch API)
                                    ▼
+-------------------------------------------------------------------------+
|                             FASTAPI BACKEND                             |
|                      (Python 3.14 + Uvicorn ASGI)                       |
+-----------------------------------+-------------------------------------+
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
  +───────────────+         +───────────────+         +───────────────+
  |  CSV Parser   |         |   Analysis    |         |   Cleaning    |
  |  & Security   |         |    Engine     |         |    Service    |
  +───────────────+         +───────────────+         +───────────────+
          │                         │                         │
          │                         ▼                         │
          │                 +───────────────+                 │
          │                 | 6 Quality     |                 │
          │                 | Analyzers     |                 │
          │                 +───────────────+                 │
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                                    ▼
+-------------------------------------------------------------------------+
|                       IN-MEMORY SESSION STORE                           |
|       (UUID4 Tokenized Sessions, 1-Hour TTL Automatic Eviction)         |
+-------------------------------------------------------------------------+
```

## Backend Modular Design

### 1. `app/utils/csv_parser.py`
- Handles character encoding fallbacks (`utf-8`, `utf-8-sig`, `latin-1`, `cp1252`, `iso-8859-1`).
- Delimiter inference (commas `,`, semicolons `;`, tabs `\t`, pipes `|`).
- Sanitizes unnamed and malformed column headers.

### 2. `app/utils/security.py`
- Enforces an upload payload limit of 15 MB.
- Path traversal mitigation via strict basename sanitization.
- Rejection of non-CSV extensions.
- In-memory execution without storing user data on disk.

### 3. `app/analyzers/`
- **`missing_analyzer.py`**: Detects standard `np.nan`/`None` and textual placeholders (`N/A`, `null`, `?`, `-`).
- **`duplicate_analyzer.py`**: Identifies full duplicate rows and provides row samples.
- **`outlier_analyzer.py`**: Implements Tukey's IQR method ($Q_3 - Q_1$) and Z-score ($|z| > 3$). Includes optional scikit-learn Isolation Forest multi-variate anomaly detection.
- **`data_type_analyzer.py`**: Inferred types (integer, float, datetime, string) and mixed-content detection.
- **`category_analyzer.py`**: Strips whitespace and groups case variants (e.g. `Chennai`, `chennai`, `CHENNAI`).
- **`column_analyzer.py`**: Flags zero-variance constant columns and quasi-constant columns ($\ge 90\%$ single value).
- **`quality_scorer.py`**: Computes an explainable, bounded hygiene score from 0 to 100.

### 4. `app/services/cleaning_service.py`
- Operates strictly on isolated working copies, preserving raw uploaded datasets.
- Interactive features:
  - Deduplication
  - Casing normalization (Title Case)
  - Missing value imputation (Mean, Median, Mode, Custom Placeholder, Row Drop)
  - Outlier handling (IQR Winsorization capping or Row Drop)
  - Column dropping

### 5. `app/services/session_store.py`
- Thread-safe singleton in-memory storage.
- Auto-expires artifacts after 1 hour (3600 seconds).
- Generates unguessable UUID4 session and download IDs.
