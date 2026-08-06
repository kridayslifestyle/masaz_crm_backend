from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.models import StoreType


class StoreBase(BaseModel):
    name: str

    owner_name: str
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None

    store_type: StoreType = StoreType.other

    city: Optional[str] = None
    address: Optional[str] = None

    is_active: bool = True

    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None

    revenue_share_type: Optional[str] = "slab_based"

    gst_number: Optional[str] = None

    account_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None

    payment_invoice: Optional[str] = None
    payment_date: Optional[date] = None

    store_username: Optional[str] = None


class StoreCreate(StoreBase):
    store_password: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None

    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None

    store_type: Optional[StoreType] = None

    city: Optional[str] = None
    address: Optional[str] = None

    is_active: Optional[bool] = None

    agreement_start_date: Optional[date] = None
    agreement_end_date: Optional[date] = None

    revenue_share_type: Optional[str] = None

    gst_number: Optional[str] = None

    store_username: Optional[str] = None
    store_password: Optional[str] = None


class StoreResponse(StoreBase):
    id: int

    created_at: datetime

    total_chairs: Optional[int] = 0

    monthly_revenue: Optional[float] = 0.0

    class Config:
        from_attributes = True

class StoreCredentialsResponse(BaseModel):
    store_username: Optional[str] = None
    store_password: Optional[str] = None