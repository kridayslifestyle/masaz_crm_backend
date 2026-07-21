from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from app.database import get_db
from app.models import Chair, Store, Collection, ChairStatus, CollectionStatus

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    today = date.today()
    month_start = today.replace(day=1)

    total_chairs = db.query(Chair).count()
    active_stores = db.query(Store).filter(Store.is_active == True).count()

    # Today's revenue
    today_revenue = (
        db.query(func.sum(Collection.total_amount))
        .filter(Collection.date == today)
        .scalar()
        or 0.0
    )

    # Monthly revenue
    monthly_revenue = (
        db.query(func.sum(Collection.total_amount))
        .filter(Collection.date >= month_start)
        .scalar()
        or 0.0
    )

    # Pending collections amount
    pending_payout_amount = (
        db.query(func.sum(Collection.total_amount))
        .filter(Collection.status == CollectionStatus.pending)
        .scalar()
        or 0.0
    )

    # Low performing chairs
    low_performing = (
        db.query(Chair).filter(Chair.status == ChairStatus.low_performing).count()
    )

    # Chair status breakdown
    chair_stats = {
        "active": db.query(Chair).filter(Chair.status == ChairStatus.active).count(),
        "low_performing": db.query(Chair)
        .filter(Chair.status == ChairStatus.low_performing)
        .count(),
        "offline": db.query(Chair).filter(Chair.status == ChairStatus.offline).count(),
        "maintenance": db.query(Chair)
        .filter(Chair.status == ChairStatus.maintenance)
        .count(),
    }

    # Last 30 days daily revenue for chart
    thirty_days_ago = today - timedelta(days=29)
    daily_rows = (
        db.query(Collection.date, func.sum(Collection.total_amount).label("revenue"))
        .filter(Collection.date >= thirty_days_ago)
        .group_by(Collection.date)
        .order_by(Collection.date)
        .all()
    )

    daily_collection_chart = [
        {"date": str(row.date), "revenue": round(row.revenue, 2)} for row in daily_rows
    ]

    # Top 5 stores by monthly revenue
    top_stores = (
        db.query(
            Store.id,
            Store.name,
            Store.city,
            func.sum(Collection.total_amount).label("monthly_revenue"),
            func.count(func.distinct(Chair.id)).label("chair_count"),
        )
        .join(Collection, Collection.store_id == Store.id)
        .join(Chair, Chair.store_id == Store.id)
        .filter(Collection.date >= month_start)
        .group_by(Store.id, Store.name, Store.city)
        .order_by(func.sum(Collection.total_amount).desc())
        .limit(5)
        .all()
    )

    top_stores_data = [
        {
            "id": s.id,
            "name": s.name,
            "city": s.city,
            "monthly_revenue": round(s.monthly_revenue, 2),
            "chair_count": s.chair_count,
        }
        for s in top_stores
    ]

    # Recent 8 collections
    recent_collections = (
        db.query(Collection).order_by(Collection.created_at.desc()).limit(8).all()
    )

    recent_data = [
        {
            "id": c.id,
            "date": str(c.date),
            "chair_code": c.chair.device_id if c.chair else None,
            "store_name": c.store.name if c.store else None,
            "total_amount": c.total_amount,
            "online_payment": c.online_payment,
            "cash_payment": c.cash_payment,
            "change_amount": c.change_amount,
            "transaction_count": c.transaction_count,
            "status": c.status,
        }
        for c in recent_collections
    ]

    return {
        "kpis": {
            "total_chairs": total_chairs,
            "active_stores": active_stores,
            "today_revenue": round(today_revenue, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "pending_payout_amount": round(pending_payout_amount, 2),
            "low_performing_chairs": low_performing,
        },
        "chair_status": chair_stats,
        "daily_collection_chart": daily_collection_chart,
        "top_stores": top_stores_data,
        "recent_collections": recent_data,
    }
