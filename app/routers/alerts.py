from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func

from app.database import get_db
from app.models import (
    Alert,
    Chair,
    Store,
    Collection
)
from app.routers import settings

router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"]
)

@router.post("/generate")
def generate_alerts(
    db: Session = Depends(get_db)
):

    today = date.today()

    generated = []

    chairs = db.query(Chair).all()

    for chair in chairs:

        revenue = (
            db.query(
                func.sum(
                    Collection.total_amount
                )
            )
            .filter(
                Collection.chair_id == chair.id,
                Collection.date == today
            )
            .scalar()
            or 0
        )

        if revenue == 0:

            alert = Alert(
                chair_id=chair.id,
                store_id=chair.store_id,
                alert_type="no_collection",
                severity="critical",
                message=(
                    f"{chair.device_id} "
                    f"has no collection today"
                )
            )

            db.add(alert)

            generated.append(
                chair.device_id
            )

        elif revenue < settings.minimum_daily_revenue:

            alert = Alert(
                chair_id=chair.id,
                store_id=chair.store_id,
                alert_type="low_revenue",
                severity="warning",
                message=(
                    f"{chair.device_id} "
                    f"generated only ₹{revenue}"
                )
            )

            db.add(alert)

            generated.append(
                chair.device_id
            )

    db.commit()

    return {
        "alerts_generated":
            len(generated),

        "machines":
            generated
    }

@router.get("")
def get_alerts(
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(Alert)
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )

    result = []

    for alert in alerts:

        result.append({
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "device_id": (
                alert.chair.device_id
                if alert.chair
                else None
            ),
            "store_name": (
                alert.store.name
                if alert.store
                else None
            ),
            "created_at": alert.created_at
        })

    return result

@router.get("/summary")
def alerts_summary(
    db: Session = Depends(get_db)
):

    total = db.query(Alert).count()

    critical = (
        db.query(Alert)
        .filter(
            Alert.severity == "critical"
        )
        .count()
    )

    warning = (
        db.query(Alert)
        .filter(
            Alert.severity == "warning"
        )
        .count()
    )

    return {
        "total_alerts": total,
        "critical": critical,
        "warning": warning
    }

@router.post("/send")
def send_alerts(
    db: Session = Depends(get_db)
):

    alerts = (
        db.query(Alert)
        .filter(
            Alert.is_sent == False
        )
        .all()
    )

    for alert in alerts:

        # Future:
        # send_whatsapp()
        # send_sms()
        # send_email()

        alert.is_sent = True

    db.commit()

    return {
        "sent": len(alerts)
    }

