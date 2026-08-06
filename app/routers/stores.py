from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Store, Chair, Collection
from sqlalchemy.exc import IntegrityError
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.dependencies.auth import get_current_user
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    StoreCredentialsResponse,
)
from app.services.credential_encryption import (
    encrypt_store_password,
    decrypt_store_password,
)

router = APIRouter(prefix="/api/stores", tags=["Stores"])


@router.get("/", response_model=List[StoreResponse])
def get_all_stores(db: Session = Depends(get_db)):
    stores = db.query(Store).filter(Store.is_active == True).all()
    result = []
    for store in stores:
        s = StoreResponse.model_validate(store)
        s.total_chairs = len(store.chairs)
        # Monthly revenue = sum of this month's collections
        from datetime import date

        today = date.today()
        monthly = (
            db.query(func.sum(Collection.total_amount))
            .filter(
                Collection.store_id == store.id,
                func.extract("month", Collection.date) == today.month,
                func.extract("year", Collection.date) == today.year,
            )
            .scalar()
            or 0.0
        )
        s.monthly_revenue = round(monthly, 2)
        result.append(s)
    return result

@router.get(
    "/{store_id}/credentials",
    response_model=StoreCredentialsResponse
)
def get_store_credentials(
    store_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only admins can reveal credentials

   


    user_role = current_user.get("role")

    if not user_role or str(user_role).lower() != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    store = (
        db.query(Store)
        .filter(Store.id == store_id)
        .first()
    )

    if not store:
        raise HTTPException(
            status_code=404,
            detail="Store not found"
        )

    password = None

    if store.store_password_encrypted:
        try:
            password = decrypt_store_password(
                store.store_password_encrypted
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Unable to decrypt store password"
            )

    return {
        "store_username": store.store_username,
        "store_password": password,
    }


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    s = StoreResponse.model_validate(store)
    s.total_chairs = len(store.chairs)
    return s


@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(
    data: StoreCreate,
    db: Session = Depends(get_db)
):
    store_data = data.model_dump(
        exclude={"store_password"}
    )

    # Check username uniqueness
    if data.store_username:
        existing_store = (
            db.query(Store)
            .filter(
                Store.store_username ==
                data.store_username
            )
            .first()
        )

        if existing_store:
            raise HTTPException(
                status_code=400,
                detail="Store username already exists"
            )

    store = Store(**store_data)

    # Encrypt password before storing
    if data.store_password:
        store.store_password_encrypted = (
            encrypt_store_password(
                data.store_password
            )
        )

    db.add(store)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Store username already exists"
        )

    db.refresh(store)

    return StoreResponse.model_validate(store)


@router.patch(
    "/{store_id}",
    response_model=StoreResponse
)
def update_store(
    store_id: int,
    data: StoreUpdate,
    db: Session = Depends(get_db)
):
    store = (
        db.query(Store)
        .filter(Store.id == store_id)
        .first()
    )

    if not store:
        raise HTTPException(
            status_code=404,
            detail="Store not found"
        )

    update_data = data.model_dump(
        exclude_unset=True,
        exclude={"store_password"}
    )

    # Check username uniqueness
    if "store_username" in update_data:
        username = update_data["store_username"]

        if username:
            existing_store = (
                db.query(Store)
                .filter(
                    Store.store_username == username,
                    Store.id != store_id
                )
                .first()
            )

            if existing_store:
                raise HTTPException(
                    status_code=400,
                    detail="Store username already exists"
                )

    for field, value in update_data.items():
        setattr(store, field, value)

    # Only replace password if admin supplied a new one
    if data.store_password:
        store.store_password_encrypted = (
            encrypt_store_password(
                data.store_password
            )
        )

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Store username already exists"
        )

    db.refresh(store)

    return StoreResponse.model_validate(store)


@router.delete("/{store_id}", status_code=204)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.is_active = False  # Soft delete
    db.commit()


@router.patch("/{store_id}/activate")
def activate_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store.is_active = True

    db.commit()

    return {"message": "Store activated"}
