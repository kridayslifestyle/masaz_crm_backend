from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import SessionLocal
from app.models import ServiceComplaint

router = APIRouter(prefix="/api/service", tags=["Service"])


class StartServiceRequest(BaseModel):
    technician_id: int


@router.patch("/{complaint_id}/start")
def start_service(complaint_id: int, data: StartServiceRequest):
    db = SessionLocal()

    complaint = db.query(ServiceComplaint).filter(
        ServiceComplaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.technician_id = data.technician_id
    complaint.status = "in_progress"

    db.commit()
    db.refresh(complaint)

    return {
        "message": "Service started",
        "data": complaint
    }