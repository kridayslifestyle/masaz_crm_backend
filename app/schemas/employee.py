from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class EmployeeBase(BaseModel):
    employee_code: str

    name: str

    phone: Optional[str] = None

    email: Optional[str] = None

    designation: Optional[str] = None

    city: Optional[str] = None

    joining_date: Optional[date] = None

    salary: Optional[float] = None

    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = None

    name: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[str] = None

    designation: Optional[str] = None

    city: Optional[str] = None

    joining_date: Optional[date] = None

    salary: Optional[float] = None

    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int

    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeSummary(BaseModel):
    total: int

    active: int

    inactive: int