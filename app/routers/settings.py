from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Settings
from app.schemas.settings import (
    SettingsResponse,
    SettingsUpdate
)

router = APIRouter(
    prefix="/api/settings",
    tags=["Settings"]
)

@router.get(
    "/",
    response_model=SettingsResponse
)
def get_settings(
    db: Session = Depends(get_db)
):

    settings = (
        db.query(Settings)
        .first()
    )

    if not settings:

        settings = Settings()

        db.add(settings)

        db.commit()

        db.refresh(settings)

    return settings

@router.put(
    "/",
    response_model=SettingsResponse
)
def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db)
):

    settings = (
        db.query(Settings)
        .first()
    )

    if not settings:

        settings = Settings()

        db.add(settings)

        db.commit()

        db.refresh(settings)

    update_data = data.model_dump()

    for field, value in update_data.items():

        setattr(
            settings,
            field,
            value
        )

    db.commit()

    db.refresh(settings)

    return settings

