"""
Excel Parser Service
--------------------
Reads uploaded chair master Excel files and returns
a list of chair dictionaries ready for DB insertion.

Expected Columns:

Device ID
Machine Number
Equipment Type
Device Grouping
Store Name
Installed Date
Status
Notes
"""

import io
from datetime import datetime

import pandas as pd
from fastapi import HTTPException


REQUIRED_COLUMNS = [
    "device_id",
    "machine_number",
]

COLUMN_MAP = {
    "device id": "device_id",
    "device_id": "device_id",

    "machine number": "machine_number",
    "machine_number": "machine_number",

    "equipment type": "equipment_type",
    "equipment_type": "equipment_type",

    "device grouping": "device_grouping",
    "device_grouping": "device_grouping",

    "store name": "store_name",
    "store_name": "store_name",

    "installed date": "installed_date",
    "installed_date": "installed_date",

    "status": "status",

    "notes": "notes",
}


def parse_excel(file_bytes: bytes) -> list[dict]:
    """
    Parse Excel file and return chair data.
    """

    try:
        df = pd.read_excel(
            io.BytesIO(file_bytes),
            engine="openpyxl"
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read Excel file: {str(e)}"
        )

    # Normalize headers
    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    # Rename columns
    rename_map = {}

    for col in df.columns:
        if col in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col]

    df = df.rename(columns=rename_map)

    # Validate required columns
    for req in REQUIRED_COLUMNS:
        if req not in df.columns:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Missing required column: '{req}'. "
                    f"Found columns: {list(df.columns)}"
                ),
            )

    # Remove empty rows
    df = df.dropna(
        subset=[
            "device_id",
            "machine_number"
        ]
    )

    df["device_id"] = (
        df["device_id"]
        .astype(str)
        .str.strip()
    )

    df["machine_number"] = (
        df["machine_number"]
        .astype(str)
        .str.strip()
    )

    chairs = []

    for _, row in df.iterrows():

        chair = {
            "device_id": str(
                row["device_id"]
            ).strip(),

            "machine_number": str(
                row["machine_number"]
            ).strip(),

            "equipment_type": str(
                row.get("equipment_type", "")
            ).strip() or None,

            "device_grouping": str(
                row.get("device_grouping", "")
            ).strip() or None,

            "store_name": str(
                row.get("store_name", "")
            ).strip() or None,

            "status": str(
                row.get("status", "active")
            ).strip().lower() or "active",

            "notes": str(
                row.get("notes", "")
            ).strip() or None,

            "installed_date": _parse_date(
                row.get("installed_date")
            ),
        }

        chairs.append(chair)

    return chairs


def _parse_date(value):

    if value is None:
        return None

    if isinstance(value, float) and pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return pd.to_datetime(
            str(value)
        ).date()

    except Exception:
        return None