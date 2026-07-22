from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, relationship
from sqlalchemy import or_, func
from typing import List, Optional

from app.database import get_db
from app.models import Chair, ChairStatus, Employee, Collection
from app.schemas.chair import (
    ChairCreate,
    ChairUpdate,
    ChairResponse,
)
from datetime import date

router = APIRouter(prefix="/api/chairs", tags=["Chairs"])


@router.get("")
def get_all_chairs(
    status: Optional[ChairStatus] = None,
    store_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    from datetime import date
    from sqlalchemy import func
    from app.models import Collection

    query = db.query(Chair)

    if status:
        query = query.filter(Chair.status == status)

    if store_id:
        query = query.filter(Chair.store_id == store_id)

    if search:
        query = query.filter(
            or_(
                Chair.device_id.ilike(f"%{search}%"),
                Chair.machine_number.ilike(f"%{search}%"),
                Chair.equipment_type.ilike(f"%{search}%"),
                Chair.device_grouping.ilike(f"%{search}%"),
            )
        )

    chairs = query.offset(skip).limit(limit).all()

    today = date.today()

    result = []

    for chair in chairs:

        daily_revenue = (
            db.query(func.sum(Collection.total_amount))
            .filter(Collection.chair_id == chair.id, Collection.date == today)
            .scalar()
            or 0
        )

        monthly_revenue = (
            db.query(func.sum(Collection.total_amount))
            .filter(
                Collection.chair_id == chair.id,
                func.extract("month", Collection.date) == today.month,
                func.extract("year", Collection.date) == today.year,
            )
            .scalar()
            or 0
        )

        if chair.installed_date:
            installed_days = (
                 today - chair.installed_date
            ).days
        else:
            installed_days = 0

        performance_score = min(round(monthly_revenue / 1000), 100)

        result.append(
            {
                "id": chair.id,
                "serial_number": chair.machine_number,
                "device_id": chair.device_id,
                "model_name": chair.equipment_type,
                "store_name": chair.store.name if chair.store else "",
                "city": chair.store.city if chair.store else "",
                "owner_name": chair.store.owner_name if chair.store else "",
                "installed_days": installed_days,
                "daily_revenue": round(daily_revenue, 2),
                "monthly_revenue": round(monthly_revenue, 2),
                "status": chair.status.value,
                "performance_score": performance_score,
            }
        )

    return result


@router.get("/{chair_id}", response_model=ChairResponse)
def get_chair(chair_id: int, db: Session = Depends(get_db)):
    chair = db.query(Chair).filter(Chair.id == chair_id).first()

    if not chair:
        raise HTTPException(status_code=404, detail="Chair not found")

    response = ChairResponse.model_validate(chair)

    response.store_name = chair.store.name if chair.store else None

    return response


@router.post("/", response_model=ChairResponse, status_code=201)
def create_chair(data: ChairCreate, db: Session = Depends(get_db)):
    if data.installed_by_employee_id:

        employee = (
            db.query(Employee)
            .filter(Employee.id == data.installed_by_employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
    existing_device = db.query(Chair).filter(Chair.device_id == data.device_id).first()

    if existing_device:
        raise HTTPException(status_code=409, detail="Device ID already exists")

    existing_machine = (
        db.query(Chair).filter(Chair.machine_number == data.machine_number).first()
    )

    if existing_machine:
        raise HTTPException(status_code=409, detail="Machine Number already exists")

    chair = Chair(**data.model_dump())

    db.add(chair)
    db.commit()
    db.refresh(chair)

    response = ChairResponse.model_validate(chair)

    response.store_name = chair.store.name if chair.store else None

    response.installed_by_employee_name = (
        chair.installed_by.name if chair.installed_by else None
    )

    maintenance_records = relationship("Maintenance", ck_populates="chair")

    return response


@router.patch("/{chair_id}", response_model=ChairResponse)
def update_chair(chair_id: int, data: ChairUpdate, db: Session = Depends(get_db)):
    chair = db.query(Chair).filter(Chair.id == chair_id).first()

    if not chair:
        raise HTTPException(status_code=404, detail="Chair not found")

    if data.installed_by_employee_id is not None:
        employee = (
            db.query(Employee)
            .filter(Employee.id == data.installed_by_employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(chair, field, value)

    db.commit()
    db.refresh(chair)

    response = ChairResponse.model_validate(chair)

    response.store_name = chair.store.name if chair.store else None

    response.installed_by_employee_name = (
        chair.installed_by.name if chair.installed_by else None
    )

    return response


@router.delete("/{chair_id}")
def delete_chair(chair_id: int, db: Session = Depends(get_db)):
    chair = db.query(Chair).filter(Chair.id == chair_id).first()

    if not chair:
        raise HTTPException(status_code=404, detail="Chair not found")

    chair.status = ChairStatus.maintenance

    db.commit()

    return {"message": "Chair moved to maintenance"}


@router.get("/stats/summary")
def chairs_summary(db: Session = Depends(get_db)):
    total = db.query(Chair).count()

    active = db.query(Chair).filter(Chair.status == ChairStatus.active).count()

    low = db.query(Chair).filter(Chair.status == ChairStatus.low_performing).count()

    offline = db.query(Chair).filter(Chair.status == ChairStatus.offline).count()

    maintenance = (
        db.query(Chair).filter(Chair.status == ChairStatus.maintenance).count()
    )

    return {
        "total": total,
        "active": active,
        "low_performing": low,
        "offline": offline,
        "maintenance": maintenance,
    }
