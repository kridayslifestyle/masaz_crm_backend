from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification
from app.services.daily_monitor import check_daily_collections

router = APIRouter(
    prefix="/api/notifications",
    tags=["Notifications"]
)

@router.get("")
def get_notifications(
    db: Session = Depends(get_db)
):
    return (
        db.query(Notification)
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

@router.get("/summary")
def notification_summary(
    db: Session = Depends(get_db)
):

    total = db.query(Notification).count()

    sent = (
        db.query(Notification)
        .filter(
            Notification.status == "sent"
        )
        .count()
    )

    pending = (
        db.query(Notification)
        .filter(
            Notification.status == "pending"
        )
        .count()
    )

    return {
        "total": total,
        "sent": sent,
        "pending": pending
    }

@router.post("/run")
def run_monitor(
    db: Session = Depends(get_db)
):

    return check_daily_collections(db)