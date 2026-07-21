from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models import PayoutStatus


class PayoutResponse(BaseModel):
    id: int

    store_id: int

    month: int
    year: int

    total_revenue: float

    applied_percentage: float

    store_share: float

    company_share: float

    status: PayoutStatus

    notes: Optional[str] = None

    generated_at: datetime

    store_name: Optional[str] = None

    class Config:
        from_attributes = True


class PayoutMarkPaid(BaseModel):
    notes: Optional[str] = None