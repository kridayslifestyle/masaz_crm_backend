from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Technician
from pydantic import BaseModel

router = APIRouter()


# ✅ SCHEMA
class TechnicianCreate(BaseModel):
    name: str
    phone: str


# ✅ GET API (already working)
@router.get("/technicians")
def get_technicians():
    db = SessionLocal()
    data = db.query(Technician).all()
    db.close()
    return data


# ✅ ADD THIS (POST API)
@router.post("/technicians")
def create_technician(data: TechnicianCreate):
    db = SessionLocal()

    new = Technician(
        name=data.name,
        phone=data.phone
    )

    db.add(new)
    db.commit()
    db.refresh(new)
    db.close()

    return new