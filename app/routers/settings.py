from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Settings
from app.schemas.settings import (
    SettingsResponse,
    SettingsUpdate,
)


router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"],
)


# ---------------------------------------------------------
# GET SETTINGS
# ---------------------------------------------------------

@router.get("/", response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
):
    settings = db.query(Settings).first()

    # Create default settings if none exist
    if not settings:
        settings = Settings(
            company_share_percentage=75,
            store_share_percentage=25,
            minimum_daily_revenue=500,
            target_daily_revenue=1000,
            alert_enabled=True,
            whatsapp_enabled=False,
            sms_enabled=False,
            email_enabled=False,
        )

        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


# ---------------------------------------------------------
# UPDATE SETTINGS
# ---------------------------------------------------------

@router.put("/", response_model=SettingsResponse)
def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
):
    # Get existing settings
    settings = db.query(Settings).first()

    # Create if no settings record exists
    if not settings:
        settings = Settings(
            company_share_percentage=75,
            store_share_percentage=25,
            minimum_daily_revenue=500,
            target_daily_revenue=1000,
            alert_enabled=True,
            whatsapp_enabled=False,
            sms_enabled=False,
            email_enabled=False,
        )

        db.add(settings)

    # Company + Store share must equal 100%
    total_share = (
        data.company_share_percentage
        + data.store_share_percentage
    )

    if abs(total_share - 100) > 0.01:
        raise HTTPException(
            status_code=400,
            detail="Company Share % and Store Share % must total 100%",
        )

    # Update values
    settings.company_share_percentage = (
        data.company_share_percentage
    )

    settings.store_share_percentage = (
        data.store_share_percentage
    )

    settings.minimum_daily_revenue = (
        data.minimum_daily_revenue
    )

    settings.target_daily_revenue = (
        data.target_daily_revenue
    )

    settings.alert_enabled = (
        data.alert_enabled
    )

    settings.whatsapp_enabled = (
        data.whatsapp_enabled
    )

    settings.sms_enabled = (
        data.sms_enabled
    )

    settings.email_enabled = (
        data.email_enabled
    )

    db.commit()
    db.refresh(settings)

    return settings