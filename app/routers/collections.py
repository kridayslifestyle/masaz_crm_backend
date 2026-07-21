from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import Collection, Chair, Store, CollectionStatus
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    RevenueSummary,
)

router = APIRouter(prefix="/api/collections", tags=["Collections"])


@router.get("/", response_model=List[CollectionResponse])
def get_collections(
    store_id: Optional[int] = None,
    chair_id: Optional[int] = None,
    status: Optional[CollectionStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    limit: int = Query(default=50, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Collection)

    if store_id:
        query = query.filter(Collection.store_id == store_id)

    if chair_id:
        query = query.filter(Collection.chair_id == chair_id)

    if status:
        query = query.filter(Collection.status == status)

    if from_date:
        query = query.filter(Collection.date >= from_date)

    if to_date:
        query = query.filter(Collection.date <= to_date)

    collections = (
        query.order_by(Collection.date.desc(), Collection.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []

    for col in collections:
        c = CollectionResponse.model_validate(col)
        c.chair_code = col.chair.device_id if col.chair else None
        c.store_name = col.store.name if col.store else None
        result.append(c)

    return result


@router.post("/", response_model=CollectionResponse, status_code=201)
def create_collection(data: CollectionCreate, db: Session = Depends(get_db)):
    chair = db.query(Chair).filter(Chair.id == data.chair_id).first()

    if not chair:
        raise HTTPException(status_code=404, detail="Chair not found")

    store = db.query(Store).filter(Store.id == data.store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    existing = (
        db.query(Collection)
        .filter(Collection.chair_id == data.chair_id, Collection.date == data.date)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Collection already exists for this chair and date"
        )

    collection = Collection(
        chair_id=data.chair_id,
        store_id=data.store_id,
        date=data.date,
        total_amount=data.total_amount,
        online_payment=data.online_payment,
        cash_payment=data.cash_payment,
        change_amount=data.change_amount,
        transaction_count=data.transaction_count,
        status=data.status,
        notes=data.notes,
    )

    db.add(collection)
    db.commit()
    db.refresh(collection)

    response = CollectionResponse.model_validate(collection)
    response.chair_code = chair.device_id
    response.store_name = store.name

    return response


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: int, data: CollectionUpdate, db: Session = Depends(get_db)
):
    col = db.query(Collection).filter(Collection.id == collection_id).first()

    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")

    if data.total_amount is not None:
        col.total_amount = data.total_amount
    
    if data.online_payment is not None:
        col.online_payment = data.online_payment
    
    if data.cash_payment is not None:
        col.cash_payment = data.cash_payment
    
    if data.change_amount is not None:
        col.change_amount = data.change_amount

    if data.transaction_count is not None:
        col.transaction_count = data.transaction_count

    if data.status is not None:
        col.status = data.status

    if data.notes is not None:
        col.notes = data.notes

    db.commit()
    db.refresh(col)

    response = CollectionResponse.model_validate(col)
    response.chair_code = col.chair.device_id if col.chair else None
    response.store_name = col.store.name if col.store else None

    return response


@router.get("/summary/totals", response_model=RevenueSummary)
def get_revenue_summary(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    store_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Collection)

    if from_date:
        query = query.filter(Collection.date >= from_date)

    if to_date:
        query = query.filter(Collection.date <= to_date)

    if store_id:
        query = query.filter(Collection.store_id == store_id)

    result = query.with_entities(
        func.sum(Collection.total_amount),
        func.count(Collection.id),
    ).first()

    return RevenueSummary(
        total_revenue=round(result[0] or 0, 2),
        collection_count=result[1] or 0,
    )
