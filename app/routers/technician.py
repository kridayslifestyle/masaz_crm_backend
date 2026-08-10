from fastapi import APIRouter
from database import SessionLocal
from models import Technician

router = APIRouter()

@router.get("/technicians")
def get_technicians():
    db = SessionLocal()
    data = db.query(Technician).all()
    return data