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
    vendor: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    total: Optional[Decimal]
    currency: str
    status: str
    review_notes: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    line_items: list[LineItemRead]


class ExtractedInvoice(BaseModel):
    """What the LLM returns. Everything optional, since documents are messy."""

    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    total: Optional[Decimal] = None
    currency: Optional[str] = None
    line_items: list[LineItemCreate] = Field(default_factory=list)
