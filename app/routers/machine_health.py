from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models import Chair, Collection

router = APIRouter(
    prefix="/api/machine-health",
    tags=["Machine Health"]
)


@router.get("")
def machine_health(
    db: Session = Depends(get_db)
):
    today = date.today()

    results = []

    chairs = db.query(Chair).all()

    for chair in chairs:

        last_collection = (
            db.query(Collection)
            .filter(
                Collection.chair_id == chair.id
            )
            .order_by(
                Collection.date.desc()
            )
            .first()
        )

        total_revenue = (
            db.query(
                func.sum(
                    Collection.total_amount
                )
            )
            .filter(
                Collection.chair_id == chair.id
            )
            .scalar()
            or 0
        )

        days_inactive = None

        if not last_collection:

            health_score = 0

        else:

            days_inactive = (
                today - last_collection.date
            ).days

            health_score = 100

            # Inactivity Penalty
            if days_inactive > 3:
                health_score -= 15

            if days_inactive > 7:
                health_score -= 15

            if days_inactive > 15:
                health_score -= 20

            if days_inactive > 30:
                health_score -= 20

            # Revenue Bonus
            if total_revenue >= 5000:
                health_score += 10

            elif total_revenue >= 2500:
                health_score += 5

            # Keep between 0 and 100
            health_score = max(
                0,
                min(100, health_score)
            )

        if health_score >= 80:
            status = "healthy"

        elif health_score >= 50:
            status = "warning"

        else:
            status = "critical"

        results.append({
            "chair_id": chair.id,
            "device_id": chair.device_id,
            "machine_number": chair.machine_number,
            "store_name": (
                chair.store.name
                if chair.store
                else None
            ),
            "last_collection_date": (
                str(last_collection.date)
                if last_collection
                else None
            ),
            "days_inactive": days_inactive,
            "health_score": health_score,
            "status": status,
            "total_revenue": round(total_revenue, 2)
        })

    return results


@router.get("/summary")
def machine_health_summary(
    db: Session = Depends(get_db)
):
    machines = machine_health(db)

    total = len(machines)

    healthy = len(
        [m for m in machines if m["status"] == "healthy"]
    )

    warning = len(
        [m for m in machines if m["status"] == "warning"]
    )

    critical = len(
        [m for m in machines if m["status"] == "critical"]
    )

    avg_health_score = (
        round(
            sum(
                m["health_score"]
                for m in machines
            ) / total,
            2
        )
        if total > 0
        else 0
    )

    return {
        "total_machines": total,
        "healthy": healthy,
        "warning": warning,
        "critical": critical,
        "avg_health_score": avg_health_score
    }