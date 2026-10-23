"""Comprehensive backend tests for API endpoints, edge cases, and data quality analyzers."""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.csv_parser import parse_csv_bytes

client = TestClient(app)

SAMPLE_CUSTOMER_CSV = """customer_id,name,age,city,annual_income,signup_date
CUST001,Aarav Sharma,28,Chennai,65000,2023-01-15
CUST002,Priya Patel,34,chennai,72000,2023-02-10
CUST003,Rohan Verma,45,CHENNAI,89000,2023-03-05
CUST004,Ananya Iyer,,Mumbai,54000,2023-04-12
CUST005,Vikram Singh,185,mumbai,98000,2023-05-18
CUST006,Neha Gupta,29,Bengaluru,,2023-06-20
CUST007,Siddharth Reddy,41,bengaluru,115000,2023-07-22
CUST008,Deepika Nair,36,Chennai,78000,2023-08-30
CUST008,Deepika Nair,36,Chennai,78000,2023-08-30
"""

SAMPLE_SALES_CSV = """order_id,product,category,quantity,price,order_date,status
ORD-1001,Wireless Mouse,Electronics,2,24.99,2024-01-05,Delivered
ORD-1002,Mechanical Keyboard,electronics,1,89.50,2024-01-06,Delivered
ORD-1003,USB-C Cable,ELECTRONICS,5,9.99,2024-01-07,Delivered
ORD-1004,Office Chair,Furniture,,199.00,2024-01-08,Delivered
ORD-1005,Standing Desk,furniture,1,450.00,2024-01-09,Delivered
ORD-1006,Coffee Mug,Kitchen,4,,2024-01-10,Delivered
ORD-1007,Water Bottle,kitchen,2,15.50,2024-01-11,Delivered
ORD-1008,Desk Lamp,Furniture,1,39.99,2024-01-12,Delivered
ORD-1008,Desk Lamp,Furniture,1,39.99,2024-01-12,Delivered
ORD-1009,Gaming Headset,Electronics,1,120.00,2024-01-13,Delivered
ORD-1010,Monitor 27-inch,ELECTRONICS,1,320.00,2024-01-14,Delivered
ORD-1011,Laptop Stand,Accessories,999,35.00,2024-01-15,Delivered
ORD-1012,HDMI Cable,Electronics,3,12.99,2024-01-16,Delivered
ORD-1013,Air Purifier,Appliances,1,149.99,2024-01-17,Delivered
ORD-1014,Noise Cancelling Earbuds,Electronics,2,79.99,2024-01-18,Delivered
ORD-1015,Electric Kettle,appliances,1,49.99,2024-01-19,Delivered
ORD-1016,Yoga Mat,Fitness,-5,29.99,2024-01-20,Delivered
"""


def test_health_check():
    """Verifies that the /api/health endpoint returns status healthy."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Smart Data Quality Analyzer" in data["service"]


def test_analyze_empty_file():
    """Verifies that an empty CSV file returns 400 Bad Request."""
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_analyze_invalid_extension():
    """Verifies that non-csv files are rejected."""
    files = {"file": ("data.txt", io.BytesIO(b"test data"), "text/plain")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 400
    assert "only comma-separated value" in response.json()["detail"].lower()


def test_analyze_valid_csv():
    """Verifies comprehensive analysis on sample customer CSV."""
    files = {"file": ("customers.csv", io.BytesIO(SAMPLE_CUSTOMER_CSV.encode("utf-8")), "text/csv")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    data = response.json()

    # Summary checks
    assert data["summary"]["total_rows"] == 9
    assert data["summary"]["total_columns"] == 6
    assert "age" in data["summary"]["column_names"]

    # Missing value detection
    missing = data["missing"]
    assert missing["total_missing_cells"] >= 2
    assert missing["columns_with_missing"] >= 2

    # Duplicate detection
    dups = data["duplicates"]
    assert dups["duplicate_row_count"] == 1
    assert len(dups["sample_duplicates"]) >= 1

    # Outlier detection
    outliers = data["outliers"]
    assert outliers["total_outliers"] >= 1
    age_outliers = [c for c in outliers["by_column"] if c["column"] == "age"]
    assert len(age_outliers) == 1
    assert age_outliers[0]["outlier_count"] >= 1

    # Category inconsistencies
    categories = data["category_consistency"]
    city_inconsistencies = [c for c in categories if c["column"] == "city"]
    assert len(city_inconsistencies) == 1
    assert len(city_inconsistencies[0]["clusters"]) >= 1

    # Score checks
    score = data["quality_score"]
    assert 0 <= score["overall_score"] <= 100
    assert "penalties" in score

    # Report retrieval
    report_id = data["report_id"]
    get_rep = client.get(f"/api/report/{report_id}")
    assert get_rep.status_code == 200
    assert get_rep.json()["report_id"] == report_id


def test_analyze_sales_data_and_constant_column():
    """Tests sales dataset which contains a 100% constant status column."""
    files = {"file": ("sales.csv", io.BytesIO(SAMPLE_SALES_CSV.encode("utf-8")), "text/csv")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    data = response.json()

    # Constant column check ('status' is 100% Delivered)
    constants = data["constant_and_low_variance"]
    status_const = [c for c in constants if c["column"] == "status"]
    assert len(status_const) == 1
    assert status_const[0]["issue_type"] == "constant"
    assert status_const[0]["top_value"] == "Delivered"

    # Outliers in quantity (999 and -5)
    outliers = data["outliers"]
    qty_outliers = [c for c in outliers["by_column"] if c["column"] == "quantity"]
    assert len(qty_outliers) == 1
    assert qty_outliers[0]["outlier_count"] >= 1


def test_cleaning_and_download():
    """Verifies cleaning operations (deduplication, category normalization, missing imputation, outlier capping)."""
    files = {"file": ("customers.csv", io.BytesIO(SAMPLE_CUSTOMER_CSV.encode("utf-8")), "text/csv")}
    analyze_res = client.post("/api/analyze", files=files)
    session_id = analyze_res.json()["session_id"]

    clean_payload = {
        "session_id": session_id,
        "remove_duplicates": True,
        "normalize_categories": True,
        "handle_missing_num": "median",
        "handle_outliers": "clip_iqr"
    }
    clean_res = client.post("/api/clean", json=clean_payload)
    assert clean_res.status_code == 200
    clean_data = clean_res.json()

    assert clean_data["original_rows"] == 9
    assert clean_data["cleaned_rows"] == 8
    assert clean_data["comparison"]["duplicate_rows"]["after"] == 0

    file_id = clean_data["file_id"]
    download_res = client.get(f"/api/download/{file_id}")
    assert download_res.status_code == 200
    assert "attachment" in download_res.headers.get("content-disposition", "")
    content = download_res.text
    lines = [l for l in content.strip().splitlines() if l.strip()]
    assert len(lines) == 9


def test_semicolon_delimited_csv():
    """Verifies that semicolon-delimited CSVs are parsed cleanly."""
    csv_text = "id;item;val\n1;pen;10\n2;book;20\n"
    files = {"file": ("data.csv", io.BytesIO(csv_text.encode("utf-8")), "text/csv")}
    response = client.post("/api/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_columns"] == 3
    assert data["summary"]["total_rows"] == 2
