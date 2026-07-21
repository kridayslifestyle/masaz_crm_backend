from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Collection, Chair, Store
from app.routers import settings

router = APIRouter(
    prefix="/api/revenue",
    tags=["Revenue Analytics"]
)

@router.get("/summary")
def revenue_summary(
    db: Session = Depends(get_db)
):
    gross_revenue = (
        db.query(
            func.sum(Collection.total_amount)
        )
        .scalar()
        or 0
    )

    company_share = (gross_revenue * settings.company_share_percentage)/100
    store_share = (gross_revenue * settings.store_share_percentage)/100
    gst = gross_revenue * 0.18

    return {
        "gross_revenue": round(gross_revenue, 2),
        "company_share": round(company_share, 2),
        "store_share": round(store_share, 2),
        "gst": round(gst, 2)
    }

@router.get("/trend")
def revenue_trend(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            Collection.date,
            func.sum(
                Collection.total_amount
            ).label("revenue")
        )
        .group_by(
            Collection.date
        )
        .order_by(
            Collection.date
        )
        .all()
    )

    return [
        {
            "date": str(row.date),
            "revenue": float(row.revenue)
        }
        for row in rows
    ]

@router.get("/top-chairs")
def top_chairs(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            Chair.device_id,
            func.sum(
                Collection.total_amount
            ).label("revenue")
        )
        .join(
            Collection,
            Collection.chair_id == Chair.id
        )
        .group_by(
            Chair.device_id
        )
        .order_by(
            func.sum(
                Collection.total_amount
            ).desc()
        )
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

@router.get("/top-stores")
def top_stores(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            Store.name,
            func.sum(
                Collection.total_amount
            ).label("revenue")
        )
        .join(
            Collection,
            Collection.store_id == Store.id
        )
        .group_by(
            Store.name
        )
        .order_by(
            func.sum(
                Collection.total_amount
            ).desc()
        )
        .all()
    )

    return [
        {
            "store_name": row.name,
            "revenue": float(row.revenue)
        }
        for row in rows
    ]

