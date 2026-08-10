from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Technician

router = APIRouter()

@router.get("/technicians")
def get_technicians():
    db = SessionLocal()
    data = db.query(Technician).all()
    return data