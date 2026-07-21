from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Employee
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)

router = APIRouter(
    prefix="/api/employees",
    tags=["Employees"]
)


@router.get("/", response_model=List[EmployeeResponse])
def get_all_employees(
    designation: Optional[str] = None,
    city: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Employee)

    if designation:
        query = query.filter(
            Employee.designation.ilike(f"%{designation}%")
        )

    if city:
        query = query.filter(
            Employee.city.ilike(f"%{city}%")
        )

    if is_active is not None:
        query = query.filter(
            Employee.is_active == is_active
        )

    if search:
        query = query.filter(
            Employee.name.ilike(f"%{search}%")
        )

    employees = (
        query
        .offset(skip)
        .limit(limit)
        .all()
    )

    return employees


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


@router.post("/", response_model=EmployeeResponse, status_code=201)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Employee)
        .filter(
            Employee.employee_code == data.employee_code
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Employee code already exists"
        )

    employee = Employee(
        **data.model_dump()
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    employee.is_active = False

    db.commit()

    return {
        "message": "Employee deactivated successfully"
    }


@router.get("/stats/summary")
def employee_summary(
    db: Session = Depends(get_db)
):
    total = db.query(Employee).count()

    active = (
        db.query(Employee)
        .filter(Employee.is_active == True)
        .count()
    )

    inactive = (
        db.query(Employee)
        .filter(Employee.is_active == False)
        .count()
    )

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
    }