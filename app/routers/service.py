from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db

from app.models import (
    ServiceComplaint,
    ServiceStatus,
    ServicePriority,
    ProblemCategory,
    Store,
    Chair,
)

from app.schemas.service import (
    ServiceComplaintCreate,
    ServiceComplaintUpdate,
    ServiceComplaintResponse,
    ServiceComplaintSummary,
)


router = APIRouter(
    prefix="/api/service",
    tags=["Service & Support"],
)


# ─────────────────────────────────────────────
# HELPER — BUILD RESPONSE
# force deploy
# ─────────────────────────────────────────────

def build_complaint_response(
    complaint: ServiceComplaint,
):
    response = ServiceComplaintResponse.model_validate(
        complaint
    )

    response.complaint_number = (
        f"SRV-{complaint.id:06d}"
    )

    if complaint.store:
        response.store_name = complaint.store.name

    if complaint.chair:
        response.chair_device_id = (
            complaint.chair.device_id
        )

        response.chair_machine_number = (
            complaint.chair.machine_number
        )

    return response


# ─────────────────────────────────────────────
# SUMMARY
# IMPORTANT: Keep this before /{complaint_id}
# ─────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=ServiceComplaintSummary,
)
def get_service_summary(
    db: Session = Depends(get_db),
):
    total = (
        db.query(ServiceComplaint)
        .count()
    )

    open_count = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.status
            == ServiceStatus.open
        )
        .count()
    )

    in_progress_count = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.status
            == ServiceStatus.in_progress
        )
        .count()
    )

    resolved_count = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.status
            == ServiceStatus.resolved
        )
        .count()
    )

    return {
        "total_complaints": total,
        "open": open_count,
        "in_progress": in_progress_count,
        "resolved": resolved_count,
    }


# ─────────────────────────────────────────────
# GET ALL COMPLAINTS
# ─────────────────────────────────────────────

@router.get(
    "/complaints",
    response_model=list[ServiceComplaintResponse],
)
def get_complaints(
    store_id: Optional[int] = None,
    chair_id: Optional[int] = None,
    status: Optional[ServiceStatus] = None,
    priority: Optional[ServicePriority] = None,
    problem_category: Optional[
        ProblemCategory
    ] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ServiceComplaint)

    if store_id is not None:
        query = query.filter(
            ServiceComplaint.store_id
            == store_id
        )

    if chair_id is not None:
        query = query.filter(
            ServiceComplaint.chair_id
            == chair_id
        )

    if status is not None:
        query = query.filter(
            ServiceComplaint.status
            == status
        )

    if priority is not None:
        query = query.filter(
            ServiceComplaint.priority
            == priority
        )

    if problem_category is not None:
        query = query.filter(
            ServiceComplaint.problem_category
            == problem_category
        )

    complaints = (
        query
        .order_by(
            ServiceComplaint.created_at.desc()
        )
        .all()
    )

    return [
        build_complaint_response(complaint)
        for complaint in complaints
    ]


# ─────────────────────────────────────────────
# CREATE COMPLAINT
# ─────────────────────────────────────────────

@router.post(
    "/complaints",
    response_model=ServiceComplaintResponse,
    status_code=201,
)
def create_complaint(
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
    if chair.store_id != store.id:
        raise HTTPException(
            status_code=400,
            detail=(
                "Selected chair does not "
                "belong to selected store"
            ),
        )

    complaint = ServiceComplaint(
        store_id=data.store_id,
        chair_id=data.chair_id,

        complaint_date=data.complaint_date,

        reported_by=data.reported_by,

        customer_name=data.customer_name,
        customer_phone=data.customer_phone,

        problem_category=(
            data.problem_category
        ),

        problem_description=(
            data.problem_description
        ),

        priority=data.priority,

        status=ServiceStatus.open,

        notes=data.notes,
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return build_complaint_response(
        complaint
    )


# ─────────────────────────────────────────────
# GET ONE COMPLAINT
# ─────────────────────────────────────────────

@router.get(
    "/complaints/{complaint_id}",
    response_model=ServiceComplaintResponse,
)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id
            == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return build_complaint_response(
        complaint
    )


# ─────────────────────────────────────────────
# UPDATE COMPLAINT
# ─────────────────────────────────────────────

@router.patch(
    "/complaints/{complaint_id}",
    response_model=ServiceComplaintResponse,
)
def update_complaint(
    complaint_id: int,
    data: ServiceComplaintUpdate,
    db: Session = Depends(get_db),
):
    complaint = (
        db.query(ServiceComplaint)
        .filter(
            ServiceComplaint.id
            == complaint_id
        )
        .first()
    )

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            complaint,
            field,
            value
        )

    db.commit()
    db.refresh(complaint)

    return build_complaint_response(
        complaint
    )