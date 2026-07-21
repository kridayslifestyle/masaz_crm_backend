from datetime import date
from sqlalchemy.orm import Session

from app.models import (
    Chair,
    Collection,
    Alert,
    Notification
)

MIN_COLLECTION = 500


def check_daily_collections(db: Session):

    today = date.today()

    chairs = db.query(Chair).all()

    created_alerts = 0

    for chair in chairs:

        today_collection = (
            db.query(Collection)
            .filter(
                Collection.chair_id == chair.id,
                Collection.date == today
            )
            .first()
        )

        amount = (
            today_collection.total_amount
            if today_collection
            else 0
        )

        if amount < MIN_COLLECTION:

            # Prevent duplicate alerts
            today_alert = (
                db.query(Alert)
                .filter(
                    Alert.chair_id == chair.id,
                    Alert.alert_type == "low_collection"
                )
                .first()
            )

            if today_alert:
                continue

            alert = Alert(
                chair_id=chair.id,
                alert_type="low_collection",
                severity="warning",
                message=f"Collected only ₹{amount}"
            )

            db.add(alert)

            msg = (
                f"Daily Collection Alert\n"
                f"Chair: {chair.device_id}\n"
                f"Store: {chair.store.name}\n"
                f"Collection: ₹{amount}\n"
                f"Expected: ₹500+\n"
                f"Action Required."
            )

            store_notification = Notification(
                chair_id=chair.id,
                store_id=chair.store_id,
                recipient_type="store_owner",
                recipient_name=chair.store.owner_name,
                recipient_phone=chair.store.owner_phone,
                message=msg,
                status="pending"
            )

            business_notification = Notification(
                chair_id=chair.id,
                store_id=chair.store_id,
                recipient_type="business_head",
                recipient_name="Management",
                recipient_phone="pending",
                message=msg,
                status="pending"
            )

            db.add(store_notification)
            db.add(business_notification)

            created_alerts += 1

    db.commit()

    return {
        "alerts_created": created_alerts
    }