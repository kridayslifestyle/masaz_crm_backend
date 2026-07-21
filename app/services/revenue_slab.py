"""
Revenue Slab Service
--------------------
Automatically calculates the store owner's revenue share percentage
based on the daily/monthly revenue generated.

Default slabs (can be overridden from DB via Settings page):
  ₹0        – ₹10,000   →  20%
  ₹10,001   – ₹15,000   →  22%
  ₹15,001   – ₹20,000   →  25%
  ₹20,001   – ₹30,000   →  28%
  ₹30,001+              →  30%
"""

from sqlalchemy.orm import Session
from app.models import RevenueSlab


# Fallback slabs if DB is empty
DEFAULT_SLABS = [
    {"min_amount": 0,      "max_amount": 10000, "percentage": 20.0, "label": "Up to ₹10,000"},
    {"min_amount": 10001,  "max_amount": 15000, "percentage": 22.0, "label": "₹10,001 – ₹15,000"},
    {"min_amount": 15001,  "max_amount": 20000, "percentage": 25.0, "label": "₹15,001 – ₹20,000"},
    {"min_amount": 20001,  "max_amount": 30000, "percentage": 28.0, "label": "₹20,001 – ₹30,000"},
    {"min_amount": 30001,  "max_amount": None,  "percentage": 30.0, "label": "Above ₹30,000"},
]


def get_store_percentage(monthly_revenue: float, db: Session) -> float:
    """
    Given a revenue amount, return the correct store owner percentage.
    Reads slabs from DB first; falls back to DEFAULT_SLABS if DB is empty.
    """
    slabs = db.query(RevenueSlab).order_by(RevenueSlab.min_amount).all()

    if not slabs:
        # Use default slabs
        for slab in DEFAULT_SLABS:
            if slab["max_amount"] is None or monthly_revenue <= slab["max_amount"]:
                return slab["percentage"]
        return DEFAULT_SLABS[-1]["percentage"]

    # Use DB slabs
    for slab in slabs:
        if slab.max_amount is None or monthly_revenue <= slab.max_amount:
            return slab.percentage

    return slabs[-1].percentage


def calculate_monthly_payout(
    monthly_revenue: float,
    db: Session
) -> dict:
    """
    Calculate final payout based on
    total monthly revenue.
    """

    if monthly_revenue < 0:
        raise ValueError(
            "Monthly revenue cannot be negative"
        )

    pct = get_store_percentage(
        monthly_revenue,
        db
    )

    store_share = round(
        monthly_revenue * (pct / 100),
        2
    )

    company_share = round(
        monthly_revenue - store_share,
        2
    )

    return {
        "total_revenue": monthly_revenue,
        "applied_percentage": pct,
        "store_share": store_share,
        "company_share": company_share,
    }


def seed_default_slabs(db: Session):
    """
    Seeds the default revenue slabs into the DB on first run.
    Call this from main.py startup event.
    """
    existing = db.query(RevenueSlab).count()
    if existing == 0:
        for slab in DEFAULT_SLABS:
            db.add(RevenueSlab(**slab))
        db.commit()

def get_slab_details(
    monthly_revenue: float,
    db: Session
):
    slabs = db.query(RevenueSlab).order_by(
        RevenueSlab.min_amount
    ).all()

    if not slabs:
        for slab in DEFAULT_SLABS:
            if (
                slab["max_amount"] is None
                or monthly_revenue <= slab["max_amount"]
            ):
                return slab

        return DEFAULT_SLABS[-1]

    for slab in slabs:
        if (
            slab.max_amount is None
            or monthly_revenue <= slab.max_amount
        ):
            return {
                "label": slab.label,
                "percentage": slab.percentage,
            }

    last = slabs[-1]

    return {
        "label": last.label,
        "percentage": last.percentage,
    }

