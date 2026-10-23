# 🛡️ Smart Data Quality Analyzer — AI & Data Science Portfolio Project

An automated, explainable data quality auditing and interactive dataset cleansing platform built with **FastAPI**, **Pandas**, **Scikit-learn**, and a modern **React + Vite** SaaS dashboard.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.14%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal)
![React](https://img.shields.io/badge/React-18-cyan)
![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen)

---

## 📌 Problem Statement

In real-world data science, machine learning models and business dashboards are only as good as the underlying data. Data scientists often spend up to **80% of their time manually inspecting, diagnosing, and cleaning tabular data** for:
- Missing cells and ambiguous placeholder strings (`"N/A"`, `"null"`, `"?"`).
- Duplicate rows that skew distributions and bias models.
- Statistical outliers that distort regression slopes and variance calculations.
- Inconsistent categorical casing (e.g., `"Chennai"`, `"chennai"`, `"CHENNAI"`).
- Constant (zero-variance) columns that contribute zero predictive signal.
- Inferred data-type mismatches (numbers and timestamps stored as text).

**Smart Data Quality Analyzer** automates this entire pre-processing audit, provides an explainable 0–100 quality score, generates actionable recommendations, and allows interactive dataset cleaning with instant CSV export.

---

## 🌟 Key Features

### 1. 🔍 Automated Quality Auditing
- **Missing Value Detection**: Detects both standard nulls and textual placeholders (`""`, `"NA"`, `"none"`, `"?"`, `"-"`).
- **Duplicate Records**: Computes duplication rates and provides sample preview records.
- **Outlier Detection**:
  - **Tukey's IQR Method** ($[Q_1 - 1.5 \times \text{IQR},\, Q_3 + 1.5 \times \text{IQR}]$).
  - **Z-Score Method** ($|z| > 3.0$).
  - **Isolation Forest (scikit-learn)** for multi-variate anomaly detection across numerical features.
- **Inconsistent Categories**: Clusters casing and whitespace discrepancies into canonical suggestions.
- **Constant & Quasi-Constant Detection**: Identifies features with zero variance or $\ge 90\%$ identical values.
- **Data Type Inference**: Detects numbers/dates stored as text and flags heterogeneous mixed-type columns.

### 2. 📊 Explainable Quality Scoring Heuristic
- Starts with a **baseline of 100 points**.
- Deducts transparent, bounded penalties across 6 dimensions:
  - Missing Values (Max 25 pts)
  - Duplicate Records (Max 20 pts)
  - Numerical Outliers (Max 15 pts)
  - Type Inconsistencies (Max 15 pts)
  - Constant Columns (Max 15 pts)
  - Category Inconsistencies (Max 10 pts)
- Displays full mathematical breakdown and qualitative letter grade (A, B, C, D, F).

### 3. 🧹 Interactive Cleansing Studio
- **Non-destructive**: The original uploaded data remains completely untouched.
- Selectively remove duplicates.
- Normalize category casing to Title Case.
- Impute missing numerical features (Mean, Median, Mode, or Row Drop).
- Impute missing categorical features (Mode, Custom Placeholder, or Row Drop).
- Treat outliers via **IQR Winsorization capping** or **Row removal**.
- Exclude zero-variance or low-information columns.
- Live before-and-after comparison matrix with one-click **Cleaned CSV Download**.

### 4. 💻 Modern SaaS UI/UX
- Responsive desktop, tablet, and mobile interface.
- One-click Light and Dark mode toggles.
- Recharts visualizations: Missing values by column, Duplicates vs Unique records, Penalty breakdown.
- Built-in synthetic demo datasets (**Customer Data** and **Sales Data**) for instant live demonstration.

---

## 🏗️ System Architecture

```
smart-data-quality-analyzer/
├── backend/
│   ├── app/
│   │   ├── analyzers/          # Missing, duplicate, outlier, type & category logic
│   │   ├── routes/             # Health, analyze, clean, report & download endpoints
│   │   ├── schemas/            # Pydantic v2 validation models
│   │   ├── services/           # Analysis engine, cleaning service & in-memory store
│   │   ├── utils/              # Robust CSV parsing & security sanitizers
│   │   └── main.py             # FastAPI entry point & CORS configuration
│   ├── tests/                  # Pytest unit & integration test suite
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # MetricCard, Dropzone, DataTable, Navbar, Sidebar
│   │   ├── pages/              # Dashboard, Analyze, Cleaning, Reports, About
│   │   ├── services/           # Fetch API service
│   │   ├── App.jsx             # Top-level state & theme coordinator
│   │   ├── main.jsx            # React root
│   │   └── index.css           # Modern SaaS design system (Light/Dark)
│   ├── package.json            # Frontend dependencies (React, Recharts, Lucide)
│   └── vite.config.js          # Vite config with backend proxy
├── sample_data/
│   ├── customer_data.csv       # Synthetic dataset with missing values, dups & outliers
│   └── sales_data.csv          # Synthetic dataset with constant column & outliers
├── docs/
│   ├── architecture.md         # Detailed architecture documentation
│   └── scoring_methodology.md  # Detailed scoring formulas & statistical rationale
└── README.md
```

---

## 🚀 Quickstart & Installation (Windows)

### Prerequisites
- **Python 3.10+** (verified on Python 3.14)
- **Node.js 18+** (verified on Node.js v24)
- **Git**

---

### Step 1: Open the Project in VS Code
Open VS Code and navigate to the project directory:
```powershell
cd "c:\Users\Admin\Documents\level 1\smart-data-quality-analyzer"
code .
```

---

### Step 2: Set Up and Run the Backend

#### Using PowerShell:
```powershell
# Navigate to backend directory
cd backend

# (Optional) Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend tests
python -m pytest tests -v

# Start FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Using Windows Command Prompt (CMD):
```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python -m pytest tests -v
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server is active at: **`http://127.0.0.1:8000`**  
Interactive Swagger API Documentation: **`http://127.0.0.1:8000/docs`**

---

### Step 3: Set Up and Run the Frontend

Open a **second terminal window**:

#### Using PowerShell or CMD:
```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```

Open your browser and navigate to: **`http://localhost:3000`**

---

## 🧪 Testing and Verification

Run the automated Pytest suite to verify all analyzers, security bounds, and endpoints:
```powershell
cd backend
python -m pytest tests -v
```

Expected output:
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_analyze_empty_file PASSED
tests/test_api.py::test_analyze_invalid_extension PASSED
tests/test_api.py::test_analyze_valid_csv PASSED
tests/test_api.py::test_analyze_sales_data_and_constant_column PASSED
tests/test_api.py::test_cleaning_and_download PASSED
tests/test_api.py::test_semicolon_delimited_csv PASSED

======================== 7 passed in 10.18s ========================
```

---

## 📡 Backend API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Backend health check and uptime timestamp |
| `POST` | `/api/analyze` | Multipart CSV upload and data quality analysis |
| `POST` | `/api/clean` | Executes selected cleaning operations on working copy |
| `GET` | `/api/report/{report_id}` | Retrieves generated audit report by UUID |
| `GET` | `/api/download/{file_id}` | Downloads cleaned dataset as a `.csv` attachment |

### Example Analysis Request via cURL:
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze" \
  -F "file=@../sample_data/customer_data.csv" \
  -F "outlier_method=iqr"
```

---

## 📋 Sample Walkthrough

1. Open **`http://localhost:3000`**.
2. Click **"Load Sample Customer Data"** on the upload page.
3. The dashboard displays:
   - **Quality Score**: 80.6 / 100 (Grade B).
   - **Missing Cells**: 2 (Age in row 4, Income in row 6).
   - **Duplicate Rows**: 1 (CUST008 duplicate).
   - **Outliers**: 1 (Age = 185).
   - **Category Casing**: Inconsistent city values (`"Chennai"`, `"chennai"`, `"CHENNAI"`).
4. Navigate to **"Clean Dataset"**:
   - Check **"Remove Duplicate Rows"**.
   - Check **"Normalize Category Labels"**.
   - Select **"Impute with Median"** for missing numbers.
   - Select **"Cap at IQR Bounds"** for outliers.
5. Click **"Execute Cleansing"**:
   - Compare rows before (9) vs after (8).
   - Missing cells drop to 0.
   - Click **"Download Cleaned CSV"** to save the sanitized dataset.

---

## 🔒 Security Best Practices
- **Payload Limits**: 15 MB file size limit protects against memory exhaustion.
- **Path Traversal Protection**: Basename extraction prevents arbitrary directory navigation.
- **Ephemeral Storage**: Datasets are held in memory only for the active session (1-hour TTL) and purged automatically.
- **Safe Serialization**: Zero exposure of raw server stack traces or local directory paths.

---

## 💡 Future Enhancements
- SQL database export (PostgreSQL / SQLite).
- Automatic column type casting to Apache Parquet format.
- Correlation matrix and collinearity detection.
- Deep anomaly detection using Autoencoders.

---

## 👨‍💻 Author & Portfolio Metadata
- **Project**: Smart Data Quality Analyzer
- **Domain**: AI & Data Science (AIDS) Engineering
- **Version**: 1.0.0 (Production-Ready Portfolio Prototype)
- **License**: MIT
