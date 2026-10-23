"""Integration test using the actual sample CSV files in sample_data directory."""

from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_customer_data_sample():
    sample_path = Path(__file__).parent.parent.parent / "sample_data" / "customer_data.csv"
    assert sample_path.exists(), f"Sample file not found at {sample_path}"

    with open(sample_path, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("customer_data.csv", f, "text/csv")})
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_rows"] == 16
    assert data["summary"]["total_columns"] == 6
    assert data["duplicates"]["duplicate_row_count"] >= 1
    assert data["missing"]["total_missing_cells"] >= 3
    assert data["outliers"]["total_outliers"] >= 1
    assert len(data["category_consistency"]) >= 1


def test_sales_data_sample():
    sample_path = Path(__file__).parent.parent.parent / "sample_data" / "sales_data.csv"
    assert sample_path.exists(), f"Sample file not found at {sample_path}"

    with open(sample_path, "rb") as f:
        response = client.post("/api/analyze", files={"file": ("sales_data.csv", f, "text/csv")})
    
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_rows"] == 17
    assert data["summary"]["total_columns"] == 7
    assert data["duplicates"]["duplicate_row_count"] >= 1
    assert len(data["constant_and_low_variance"]) >= 1
    assert data["outliers"]["total_outliers"] >= 1
