from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from fastapi import HTTPException

from app.database import get_db
from app.models import Maintenance

router = APIRouter(
    prefix="/api/maintenance",
    tags=["Maintenance"]
)

@router.post("/")
def create_maintenance(
    chair_id: int,
    issue_type: str,
    description: str,
    priority: str = "medium",
    db: Session = Depends(get_db)
):

    record = Maintenance(
        chair_id=chair_id,
        issue_type=issue_type,
        description=description,
        reported_date=date.today(),
        priority=priority,
        status="open"
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record

@router.get("/")
def get_maintenance(
    db: Session = Depends(get_db)
):

    return db.query(
        Maintenance
    ).all()

@router.put("/{maintenance_id}/close")
def close_ticket(
    maintenance_id: int,
    db: Session = Depends(get_db)
):

    ticket = (
        db.query(Maintenance)
        .filter(
            Maintenance.id == maintenance_id
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    ticket.status = "resolved"
    ticket.resolved_date = date.today()

    db.commit()

    return {
        "message": "Maintenance closed"
    }

@router.get("/summary")
def maintenance_summary(
    db: Session = Depends(get_db)
):

    total = db.query(
        Maintenance
    ).count()

    open_count = (
        db.query(Maintenance)
        .filter(
            Maintenance.status == "open"
        )
        .count()
    )

    resolved_count = (
        db.query(Maintenance)
        .filter(
            Maintenance.status == "resolved"
        )
        .count()
    )

    return {
        "total_tickets": total,
        "open": open_count,
        "resolved": resolved_count
    }

