from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models import CollectionStatus


class CollectionCreate(BaseModel):
    chair_id: int
    store_id: int

    date: date

    total_amount: float

    online_payment: float = 0

    cash_payment: float = 0

    change_amount: float = 0

    transaction_count: int = 0

    status: CollectionStatus = CollectionStatus.pending

    notes: Optional[str] = None


class CollectionUpdate(BaseModel):
    total_amount: Optional[float] = None

    online_payment: Optional[float] = None

    cash_payment: Optional[float] = None

    change_amount: Optional[float] = None

    transaction_count: Optional[int] = None

    status: Optional[CollectionStatus] = None

    notes: Optional[str] = None


class CollectionResponse(BaseModel):
    id: int

    chair_id: int

    store_id: int

    date: date

    total_amount: float

    online_payment: float

    cash_payment: float

    change_amount: float

    transaction_count: int

    status: CollectionStatus

    notes: Optional[str] = None

    created_at: datetime

    chair_code: Optional[str] = None

    store_name: Optional[str] = None

    class Config:
        from_attributes = True


class RevenueSummary(BaseModel):
    total_revenue: float

    collection_count: int