from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models import Collection, Chair, Store
from app.routers import settings

router = APIRouter(
    prefix="/api/revenue",
    tags=["Revenue Analytics"]
)


def apply_date_filter(query, type, start_date, end_date):
    if type == "today":
        today = date.today()
        query = query.filter(Collection.date == today)

    elif start_date and end_date:
        query = query.filter(
            Collection.date >= start_date,
            Collection.date <= end_date
        )

    return query


# ===========================
# ✅ SUMMARY API
# ===========================
@router.get("/summary")
def revenue_summary(
    type: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Collection)

    query = apply_date_filter(query, type, start_date, end_date)

    gross_revenue = (
        query.with_entities(func.sum(Collection.total_amount)).scalar()
        or 0
    )

    company_share = (gross_revenue * settings.company_share_percentage) / 100
    store_share = (gross_revenue * settings.store_share_percentage) / 100
    gst = gross_revenue * 0.18

    return {
        "gross_revenue": round(gross_revenue, 2),
        "company_share": round(company_share, 2),
        "store_share": round(store_share, 2),
        "gst": round(gst, 2)
    }


# ===========================
# ✅ TREND API
# ===========================
@router.get("/trend")
def revenue_trend(
    type: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        Collection.date,
        func.sum(Collection.total_amount).label("revenue")
    )

    query = apply_date_filter(query, type, start_date, end_date)

    rows = (
        query.group_by(Collection.date)
        .order_by(Collection.date)
        .all()
    )

    return [
        {
            "date": str(row.date),
            "revenue": float(row.revenue)
        }
        for row in rows
    ]


# ===========================
# ✅ TOP CHAIRS
# ===========================
@router.get("/top-chairs")
def top_chairs(
    type: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        Chair.device_id,
        func.sum(Collection.total_amount).label("revenue")
    ).join(
        Collection,
        Collection.chair_id == Chair.id
    )

    query = apply_date_filter(query, type, start_date, end_date)

    rows = (
        query.group_by(Chair.device_id)
        .order_by(func.sum(Collection.total_amount).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "device_id": row.device_id,
            "revenue": float(row.revenue)
        }
        for row in rows
    ]


# ===========================
# ✅ TOP STORES
# ===========================
@router.get("/top-stores")
def top_stores(
    type: str = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(
        Store.name,
        func.sum(Collection.total_amount).label("revenue")
    ).join(
        Collection,
        Collection.store_id == Store.id
    )

    query = apply_date_filter(query, type, start_date, end_date)

    rows = (
        query.group_by(Store.name)
        .order_by(func.sum(Collection.total_amount).desc())
        .all()
    )

    return [
        {
            "store_name": row.name,
            "revenue": float(row.revenue)
        }
        for row in rows
    ]