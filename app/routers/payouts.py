from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import get_db
from app.models import (
    Payout,
    Store,
    Collection,
    PayoutStatus,
)
from app.schemas.payout import (
    PayoutResponse,
    PayoutMarkPaid,
)
from app.services.revenue_slab import (
    calculate_monthly_payout,
)

router = APIRouter(
    prefix="/api/payouts",
    tags=["Payouts"]
)


@router.post("/generate")
def generate_monthly_payouts(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):
    stores = db.query(Store).filter(
        Store.is_active == True
    ).all()

    generated = []

    for store in stores:

        existing = db.query(Payout).filter(
            Payout.store_id == store.id,
            Payout.month == month,
            Payout.year == year,
        ).first()

        if existing:
            continue

        monthly_revenue = (
            db.query(
                func.sum(Collection.total_amount)
            )
            .filter(
                Collection.store_id == store.id,
                func.extract("month", Collection.date) == month,
                func.extract("year", Collection.date) == year,
            )
            .scalar()
            or 0
        )

        if monthly_revenue <= 0:
            continue

        payout_data = calculate_monthly_payout(
            monthly_revenue,
            db
        )

        payout = Payout(
            store_id=store.id,
            month=month,
            year=year,
            total_revenue=payout_data["total_revenue"],
            applied_percentage=payout_data["applied_percentage"],
            store_share=payout_data["store_share"],
            company_share=payout_data["company_share"],
            status=PayoutStatus.pending,
        )

        db.add(payout)

        generated.append(
            {
                "store": store.name,
                "revenue": monthly_revenue,
            }
        )

    db.commit()

    return {
        "message": "Payout generation completed",
        "generated_count": len(generated),
        "generated": generated,
    }


@router.get("/", response_model=list[PayoutResponse])
def get_payouts(
    db: Session = Depends(get_db)
):
    payouts = (
        db.query(Payout)
        .order_by(
            Payout.year.desc(),
            Payout.month.desc()
        )
        .all()
    )

    result = []

    for payout in payouts:
        p = PayoutResponse.model_validate(
            payout
        )

        p.store_name = (
            payout.store.name
            if payout.store
            else None
        )

        result.append(p)

    return result


@router.get("/{payout_id}", response_model=PayoutResponse)
def get_payout(
    payout_id: int,
    db: Session = Depends(get_db)
):
    payout = (
        db.query(Payout)
        .filter(Payout.id == payout_id)
        .first()
    )

    if not payout:
        raise HTTPException(
            status_code=404,
            detail="Payout not found"
        )

    response = PayoutResponse.model_validate(
        payout
    )

    response.store_name = (
        payout.store.name
        if payout.store
        else None
    )

    return response


@router.patch("/{payout_id}/mark-paid")
def mark_payout_paid(
    payout_id: int,
    data: PayoutMarkPaid,
    db: Session = Depends(get_db)
):
    payout = (
        db.query(Payout)
        .filter(Payout.id == payout_id)
        .first()
    )

    if not payout:
        raise HTTPException(
            status_code=404,
            detail="Payout not found"
        )

    payout.status = PayoutStatus.paid

    if data.notes:
        payout.notes = data.notes

    db.commit()

    return {
        "message": "Payout marked as paid"
    }