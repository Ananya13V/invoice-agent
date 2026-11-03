from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LineItemCreate(BaseModel):
    description: str
    quantity: Decimal = Decimal("1")
    unit_price: Decimal


class LineItemRead(LineItemCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InvoiceCreate(BaseModel):
    vendor: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total: Decimal
    currency: str = Field(default="USD", min_length=3, max_length=3)
    line_items: list[LineItemCreate] = Field(default_factory=list)


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vendor: str
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    total: Decimal
    currency: str
    status: str
    file_path: Optional[str]
    created_at: datetime
    line_items: list[LineItemRead]
