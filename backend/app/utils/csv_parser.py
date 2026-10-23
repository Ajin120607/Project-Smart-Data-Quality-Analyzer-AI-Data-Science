"""Robust CSV parsing and encoding detection utility."""

import io
from typing import Tuple
import pandas as pd
from fastapi import HTTPException, status

ENCODINGS_TO_TRY = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]


def parse_csv_bytes(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, str]:
    """
    Parses raw bytes of an uploaded CSV into a pandas DataFrame.
    Tries multiple encodings and infers delimiters gracefully.
    
    Returns:
        Tuple of (pd.DataFrame, detected_encoding)
    """
    decoded_text = None
    detected_encoding = None

    # Step 1: Detect and decode encoding
    for enc in ENCODINGS_TO_TRY:
        try:
            decoded_text = file_bytes.decode(enc)
            detected_encoding = enc
            break
        except UnicodeDecodeError:
            continue

    if decoded_text is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode CSV file. The file appears to use an unsupported character encoding."
        )

    # Check for empty content or whitespace only
    stripped = decoded_text.strip()
    if not stripped:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file contains only empty or whitespace content."
        )

    # Step 2: Try parsing with pandas with flexible delimiter detection
    delimiters_to_try = [None, ',', ';', '\t', '|']
    df = None
    parse_error_msg = ""

    for delim in delimiters_to_try:
        try:
            string_io = io.StringIO(decoded_text)
            if delim is None:
                # Let pandas' python engine detect separator using csv.Sniffer
                df = pd.read_csv(
                    string_io,
                    sep=None,
                    engine="python",
                    on_bad_lines="skip"
                )
            else:
                df = pd.read_csv(
                    string_io,
                    sep=delim,
                    engine="python",
                    on_bad_lines="skip"
                )

            # Check if dataframe has at least 1 column
            if df is not None and len(df.columns) > 0:
                break
        except Exception as e:
            parse_error_msg = str(e)
            continue

    if df is None or len(df.columns) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse CSV dataset: {parse_error_msg or 'Malformed or empty structure'}"
        )

    # Clean column names: strip whitespace, ensure strings, handle unnamed columns
    clean_columns = []
    for idx, col in enumerate(df.columns):
        col_str = str(col).strip()
        if not col_str or col_str.startswith("Unnamed:"):
            clean_columns.append(f"column_{idx + 1}")
        else:
            clean_columns.append(col_str)
    
    df.columns = clean_columns

    if len(df) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV contains column headers but zero data rows."
        )

    return df, detected_encoding
