from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models import ChairStatus


class ChairBase(BaseModel):
    device_id: str

    machine_number: str

    equipment_type: Optional[str] = None

    device_grouping: Optional[str] = None

    status: ChairStatus = ChairStatus.active

    store_id: Optional[int] = None

    installed_by_employee_id: Optional[int] = None

    installed_date: Optional[date] = None

    last_maintenance: Optional[date] = None

    notes: Optional[str] = None


class ChairCreate(ChairBase):
    pass


class ChairUpdate(BaseModel):
    device_id: Optional[str] = None

    machine_number: Optional[str] = None

    equipment_type: Optional[str] = None

    device_grouping: Optional[str] = None

    status: Optional[ChairStatus] = None

    store_id: Optional[int] = None

    installed_by_employee_id: Optional[int] = None

    installed_date: Optional[date] = None

    last_maintenance: Optional[date] = None

    notes: Optional[str] = None


class ChairResponse(ChairBase):
    id: int

    created_at: datetime

    store_name: Optional[str] = None

    installed_by_employee_name: Optional[str] = None

    class Config:
        from_attributes = True