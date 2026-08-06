from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from app.models import (
    ServiceStatus,
    ServicePriority,
    ProblemCategory,
)


# ─────────────────────────────────────────────
# BASE
# ─────────────────────────────────────────────

class ServiceComplaintBase(BaseModel):

    store_id: int
    chair_id: int

    complaint_date: date

    reported_by: Optional[str] = None

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

    problem_category: ProblemCategory

    problem_description: str

    priority: ServicePriority = ServicePriority.medium

    notes: Optional[str] = None


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

class ServiceComplaintCreate(
    ServiceComplaintBase
):
    pass


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

class ServiceComplaintUpdate(BaseModel):

    reported_by: Optional[str] = None

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

    problem_category: Optional[
        ProblemCategory
    ] = None

    problem_description: Optional[
        str
    ] = None

    priority: Optional[
        ServicePriority
    ] = None

    status: Optional[
        ServiceStatus
    ] = None

    technician_name: Optional[str] = None

    visit_date: Optional[date] = None

    actual_problem: Optional[str] = None

    resolution_details: Optional[str] = None

    parts_replaced: Optional[str] = None

    service_cost: Optional[
        float
    ] = Field(default=None, ge=0)

    resolution_date: Optional[date] = None

    notes: Optional[str] = None


# ─────────────────────────────────────────────
# RESPONSE
# ─────────────────────────────────────────────

class ServiceComplaintResponse(
    ServiceComplaintBase
):

    id: int

    status: ServiceStatus

    technician_name: Optional[str] = None

    visit_date: Optional[date] = None

    actual_problem: Optional[str] = None

    resolution_details: Optional[str] = None

    parts_replaced: Optional[str] = None

    service_cost: Optional[float] = None

    resolution_date: Optional[date] = None

    created_at: datetime

    updated_at: Optional[datetime] = None

    # Display information populated by router
    complaint_number: Optional[str] = None

    store_name: Optional[str] = None

    chair_device_id: Optional[str] = None

    chair_machine_number: Optional[str] = None

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────

class ServiceComplaintSummary(BaseModel):

    total_complaints: int

    open: int

    in_progress: int

    resolved: int