from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Store, Chair, Collection
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse

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
        monthly = db.query(func.sum(Collection.total_amount)).filter(
            Collection.store_id == store.id,
            func.extract("month", Collection.date) == today.month,
            func.extract("year", Collection.date) == today.year,
        ).scalar() or 0.0
        s.monthly_revenue = round(monthly, 2)
        result.append(s)
    return result


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    s = StoreResponse.model_validate(store)
    s.total_chairs = len(store.chairs)
    return s


@router.post("/", response_model=StoreResponse, status_code=201)
def create_store(data: StoreCreate, db: Session = Depends(get_db)):
    store = Store(**data.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return StoreResponse.model_validate(store)


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(store_id: int, data: StoreUpdate, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return StoreResponse.model_validate(store)


@router.delete("/{store_id}", status_code=204)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    store.is_active = False   # Soft delete
    db.commit()

@router.patch("/{store_id}/activate")
def activate_store(
    store_id: int,
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

    store.is_active = True

    db.commit()

    return {
        "message": "Store activated"
    }

