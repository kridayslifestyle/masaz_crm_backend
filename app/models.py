from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ChairStatus(str, enum.Enum):
    active = "active"
    low_performing = "low_performing"
    offline = "offline"
    maintenance = "maintenance"


class CollectionStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"


class StoreType(str, enum.Enum):
    salon = "salon"
    restaurant = "restaurant"
    beauty_parlour = "beauty_parlour"
    spa = "spa"
    hospital = "hospital"
    mall = "mall"
    other = "other"


# ── Store ──────────────────────────────────────────────────────────────────────
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    owner_phone = Column(String)
    owner_email = Column(String)
    store_type = Column(Enum(StoreType), default=StoreType.other)
    city = Column(String)
    address = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    agreement_start_date = Column(Date, nullable=True)
    agreement_end_date = Column(Date, nullable=True)

    revenue_share_type = Column(String, default="slab_based")

    gst_number = Column(String, nullable=True)

    # Relationships
    chairs = relationship("Chair", back_populates="store")
    collections = relationship("Collection", back_populates="store")

    payouts = relationship("Payout", back_populates="store")


# ── Chair ──────────────────────────────────────────────────────────────────────
class Chair(Base):
    __tablename__ = "chairs"

    id = Column(Integer, primary_key=True, index=True)

    # From MasaZ machine reports
    device_id = Column(String, unique=True, nullable=False, index=True)

    machine_number = Column(String, unique=True, nullable=False, index=True)

    equipment_type = Column(String, nullable=True)

    device_grouping = Column(String, nullable=True)

    status = Column(Enum(ChairStatus), default=ChairStatus.active)

    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)

    installed_by_employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=True
    )

    installed_date = Column(Date, nullable=True)

    last_maintenance = Column(Date, nullable=True)

    notes = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    # Relationships
    store = relationship(
        "Store",
        back_populates="chairs"
    )

    collections = relationship(
        "Collection",
        back_populates="chair"
    )

    installed_by = relationship(
        "Employee"
    )

    maintenance_records = relationship(
        "Maintenance",
        back_populates="chair",
        cascade="all, delete-orphan"
    )


# ── Collection (daily revenue entry) ──────────────────────────────────────────
class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    chair_id = Column(Integer, ForeignKey("chairs.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)

    online_payment = Column(Float, default=0)

    cash_payment = Column(Float, default=0)

    change_amount = Column(Float, default=0)

    transaction_count = Column(Integer, default=0)

    status = Column(Enum(CollectionStatus), default=CollectionStatus.pending)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chair = relationship("Chair", back_populates="collections")
    store = relationship("Store", back_populates="collections")


# ── Revenue Slab config (stored in DB so you can edit from settings page) ─────
class RevenueSlab(Base):
    __tablename__ = "revenue_slabs"

    id = Column(Integer, primary_key=True, index=True)
    min_amount = Column(Float, nullable=False)  # e.g. 0
    max_amount = Column(Float, nullable=True)  # None = infinity (last slab)
    percentage = Column(Float, nullable=False)  # e.g. 20.0
    label = Column(String)  # e.g. "Up to ₹10,000"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PayoutStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)

    store_id = Column(Integer, ForeignKey("stores.id"))

    month = Column(Integer)
    year = Column(Integer)

    total_revenue = Column(Float)

    applied_percentage = Column(Float)

    store_share = Column(Float)

    company_share = Column(Float)

    status = Column(Enum(PayoutStatus), default=PayoutStatus.pending)

    notes = Column(String, nullable=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    store = relationship("Store", back_populates="payouts")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    employee_code = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)

    phone = Column(String)

    email = Column(String)

    designation = Column(String)

    city = Column(String)

    joining_date = Column(Date)

    salary = Column(Float)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    chair_id = Column(
        Integer,
        ForeignKey("chairs.id"),
        nullable=False
    )

    issue_type = Column(String, nullable=False)

    description = Column(Text)

    reported_date = Column(Date)

    resolved_date = Column(Date)

    status = Column(
        String,
        default="open"
    )

    priority = Column(
        String,
        default="medium"
    )

    chair = relationship(
        "Chair",
        back_populates="maintenance_records"
    )

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chair_id = Column(
        Integer,
        ForeignKey("chairs.id"),
        nullable=True
    )

    store_id = Column(
        Integer,
        ForeignKey("stores.id"),
        nullable=True
    )

    alert_type = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_sent = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    chair = relationship("Chair")

    store = relationship("Store")

class Settings(Base):
    __tablename__ = "settings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_share_percentage = Column(
        Float,
        default=75
    )

    store_share_percentage = Column(
        Float,
        default=25
    )

    minimum_daily_revenue = Column(
        Float,
        default=500
    )

    target_daily_revenue = Column(
        Float,
        default=1000
    )

    alert_enabled = Column(
        Boolean,
        default=True
    )

    whatsapp_enabled = Column(
        Boolean,
        default=False
    )

    sms_enabled = Column(
        Boolean,
        default=False
    )

    email_enabled = Column(
        Boolean,
        default=False
    )

class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        default=UserRole.manager
    )

    is_active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chair_id = Column(
        Integer,
        ForeignKey("chairs.id")
    )

    store_id = Column(
        Integer,
        ForeignKey("stores.id")
    )

    recipient_type = Column(
        String
    )  # store_owner / business_head

    recipient_name = Column(
        String
    )

    recipient_phone = Column(
        String
    )

    message = Column(
        Text
    )

    channel = Column(
        String,
        default="pending"
    )  # sms / whatsapp / email

    status = Column(
        String,
        default="pending"
    )  # pending / sent / failed

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    chair = relationship("Chair")
    store = relationship("Store")