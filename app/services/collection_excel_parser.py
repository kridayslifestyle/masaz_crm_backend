import pandas as pd
from fastapi import HTTPException
from datetime import datetime
import io

COLUMN_MAP = {
    "statistical date": "date",
    "device id": "device_id",
    "equipment type": "equipment_type",
    "machine number": "machine_number",
    "device grouping": "device_grouping",
    "store name": "store_name",
    "total amount": "total_amount",
    "online payment": "online_payment",
    "cash payment": "cash_payment",
    "change amount": "change_amount",
    "number of online payments": "online_payment_count",
    "other payment amounts": "other_payment",
    "offline coin": "offline_coin",
    "online coin": "online_coin",
    "number of rounds started": "transaction_count",
    "prizes won": "prizes_won",
}


REQUIRED_COLUMNS = [
    "date",
    "device_id",
    "store_name",
    "total_amount",
]


def parse_collection_excel(file_bytes: bytes):
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Could not read Excel file: {str(e)}"
        )

    df.columns = [" ".join(str(col).strip().lower().split()) for col in df.columns]

    rename = {}

    for col in df.columns:
        if col in COLUMN_MAP:
            rename[col] = COLUMN_MAP[col]

    df = df.rename(columns=rename)

    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise HTTPException(
                status_code=422, detail=f"Missing required column: {col}"
            )

    rows = []

    for _, row in df.iterrows():

        rows.append(
            {
                "date": _parse_date(row.get("date")),
                "device_id": str(row.get("device_id", "")).strip(),
                "store_name": str(row.get("store_name", "")).strip(),
                "total_amount": safe_float(row.get("total_amount")),
                "online_payment": safe_float(row.get("online_payment")),
                "cash_payment": safe_float(row.get("cash_payment")),
                "change_amount": safe_float(row.get("change_amount")),
                "transaction_count": safe_int(row.get("transaction_count")),
            }
        )

    return rows


def _parse_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def safe_float(value):
    if pd.isna(value):
        return 0.0

    try:
        return float(value)
    except Exception:
        return 0.0


def safe_int(value):
    if pd.isna(value):
        return 0

    try:
        return int(float(value))
    except Exception:
        return 0
