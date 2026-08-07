from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models import (
    ServiceComplaint,
    Store,
    Chair,
    ServiceStatus,
    ServicePriority,
)

from app.schemas.service import (
    ServiceComplaintCreate,
    ServiceComplaintUpdate,
    ServiceComplaintResponse,
)


router = APIRouter(
    prefix="/api/service",
    tags=["Service Management"],
)


# ---------------------------------------------------------
# GET ALL COMPLAINTS
# ---------------------------------------------------------

@router.get("/")
def get_service_complaints(
    status: Optional[ServiceStatus] = None,
    priority: Optional[ServicePriority] = None,
    store_id: Optional[int] = None,
    chair_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ServiceComplaint)

    if status:
        query = query.filter(
            ServiceComplaint.status == status
        )

    if priority:
        query = query.filter(
            ServiceComplaint.priority == priority
        )

    if store_id:
        query = query.filter(
            ServiceComplaint.store_id == store_id
        )

    if chair_id:
        query = query.filter(
            ServiceComplaint.chair_id == chair_id
        )

    complaints = (
        query
        .order_by(ServiceComplaint.created_at.desc())
        .all()
    )

    result = []

    for complaint in complaints:

        result.append({
            "id": complaint.id,

            "store_id": complaint.store_id,
            "store_name":
                complaint.store.name
                if complaint.store
                else None,

            "chair_id": complaint.chair_id,
            "machine_number":
                complaint.chair.machine_number
                if complaint.chair
                else None,

            "device_id":
                complaint.chair.device_id
                if complaint.chair
                else None,

            "complaint_date":
                complaint.complaint_date,

            "reported_by":
                complaint.reported_by,

            "customer_name":
                complaint.customer_name,

            "customer_phone":
                complaint.customer_phone,

            "problem_category":
                complaint.problem_category.value,

            "problem_description":
                complaint.problem_description,

            "priority":
                complaint.priority.value,

            "status":
                complaint.status.value,

            "technician_name":
                complaint.technician_name,

            "visit_date":
                complaint.visit_date,

            "actual_problem":
                complaint.actual_problem,

            "resolution_details":
                complaint.resolution_details,

            "parts_replaced":
                complaint.parts_replaced,

            "service_cost":
                complaint.service_cost,

            "resolution_date":
                complaint.resolution_date,

            "notes":
                complaint.notes,

            "created_at":
                complaint.created_at,
        })

    return result


# ---------------------------------------------------------
# GET SINGLE COMPLAINT
# ---------------------------------------------------------

@router.get("/{complaint_id}")
def get_service_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Service complaint not found",
        )

    return complaint


# ---------------------------------------------------------
# CREATE COMPLAINT
# ---------------------------------------------------------

@router.post("/", status_code=201)
def create_service_complaint(
    data: ServiceComplaintCreate,
    db: Session = Depends(get_db),
):

    # Check store

    store = (
        db.query(Store)
        .filter(Store.id == data.store_id)
        .first()
    )

    if not store:
        raise HTTPException(
            status_code=404,
            detail="Store not found",
        )

    # Check chair

    chair = (
        db.query(Chair)
        .filter(Chair.id == data.chair_id)
        .first()
    )

    if not chair:
        raise HTTPException(
            status_code=404,
            detail="Chair not found",
        )

    # Important:
    # selected chair must belong to selected store

    if chair.store_id != data.store_id:
        raise HTTPException(
            status_code=400,
            detail="Selected chair does not belong to selected store",
        )

    complaint = ServiceComplaint(
        **data.model_dump()
    )

    db.add(complaint)

    db.commit()

    db.refresh(complaint)

    return complaint


# ---------------------------------------------------------
# UPDATE COMPLAINT
# ---------------------------------------------------------

@router.patch("/{complaint_id}")
def update_service_complaint(
    complaint_id: int,
    data: ServiceComplaintUpdate,
    db: Session = Depends(get_db),
):

    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Service complaint not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            complaint,
            field,
            value,
        )

    db.commit()

    db.refresh(complaint)

    return complaint


# ---------------------------------------------------------
# MARK IN PROGRESS
# ---------------------------------------------------------

@router.patch("/{complaint_id}/start")
def start_service(
    complaint_id: int,
    db: Session = Depends(get_db),
):

    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Service complaint not found",
        )

    complaint.status = ServiceStatus.in_progress

    db.commit()

    return {
        "message": "Service marked as in progress"
    }


# ---------------------------------------------------------
# RESOLVE COMPLAINT
# ---------------------------------------------------------

@router.patch("/{complaint_id}/resolve")
def resolve_service(
    complaint_id: int,
    data: ServiceComplaintUpdate,
    db: Session = Depends(get_db),
):

    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Service complaint not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            complaint,
            field,
            value,
        )

    complaint.status = ServiceStatus.resolved

    if not complaint.resolution_date:
        complaint.resolution_date = date.today()

    db.commit()

    db.refresh(complaint)

    return complaint