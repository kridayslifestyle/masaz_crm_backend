from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models import Employee, Chair, Collection

router = APIRouter(
    prefix="/api/incentives",
    tags=["Incentives"]
)

