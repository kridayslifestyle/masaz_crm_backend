from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models import Employee, Chair, Collection, Store

router = APIRouter(
    prefix="/api/employees",
    tags=["Employee Performance"]
)


@router.get("/stats/performance")
def employee_performance(
    db: Session = Depends(get_db)
):
    today = date.today()

    results = []

    employees = db.query(Employee).all()

    for employee in employees:

        # ✅ CHAIRS INSTALLED
        chairs_installed = (
            db.query(Chair)
            .filter(Chair.installed_by_employee_id == employee.id)
            .count()
        )

        # ✅ ACTIVE CHAIRS
        active_chairs = (
            db.query(Chair)
            .filter(
                Chair.installed_by_employee_id == employee.id,
                Chair.status == "active"
            )
            .count()
        )

        # ✅ MONTHLY REVENUE
        monthly_revenue = (
            db.query(func.sum(Collection.total_amount))
            .join(Chair, Chair.id == Collection.chair_id)
            .filter(
                Chair.installed_by_employee_id == employee.id,
                func.extract("month", Collection.date) == today.month,
                func.extract("year", Collection.date) == today.year
            )
            .scalar() or 0
        )

        # ✅ TOTAL REVENUE
        total_revenue = (
            db.query(func.sum(Collection.total_amount))
            .join(Chair, Chair.id == Collection.chair_id)
            .filter(
                Chair.installed_by_employee_id == employee.id
            )
            .scalar() or 0
        )

        # 🔥 NEW: STORE-WISE DATA
        store_rows = (
            db.query(
                Store.name,
                func.count(Chair.id).label("chair_count")
            )
            .join(Chair, Chair.store_id == Store.id)
            .filter(
                Chair.installed_by_employee_id == employee.id
            )
            .group_by(Store.name)
            .all()
        )

        stores = [
            {
                "store_name": row.name,
                "chairs": row.chair_count
            }
            for row in store_rows
        ]

        results.append({
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "employee_name": employee.name,
            "designation": employee.designation,

            "chairs_installed": chairs_installed,
            "active_chairs": active_chairs,

            "monthly_revenue": round(monthly_revenue, 2),
            "total_revenue": round(total_revenue, 2),

            # 🔥 NEW FIELDS
            "stores": stores,
            "total_stores": len(stores)
        })

    return results