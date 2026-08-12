from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    company_share_percentage: float
    store_share_percentage: float
    minimum_daily_revenue: float
    target_daily_revenue: float

    alert_enabled: bool

    whatsapp_enabled: bool
    sms_enabled: bool
    email_enabled: bool

    class Config:
        from_attributes = True


class SettingsUpdate(BaseModel):
    company_share_percentage: float = Field(
        ge=0,
        le=100
    )

    store_share_percentage: float = Field(
        ge=0,
        le=100
    )

    minimum_daily_revenue: float = Field(
        ge=0
    )

    target_daily_revenue: float = Field(
        ge=0
    )

    alert_enabled: bool

    whatsapp_enabled: bool
    sms_enabled: bool
    email_enabled: bool