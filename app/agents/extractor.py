from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.config import settings
from app.schemas import ExtractedInvoice

client = genai.Client(api_key=settings.gemini_api_key)

MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}

PROMPT = (
    "Extract the invoice data from this document. Use null for anything you "
    "cannot find; never guess. Dates as YYYY-MM-DD, currency as a 3-letter code, "
    "amounts as plain numbers without currency symbols."
)


# Gemini's schema support is simpler than Pydantic's, so the model returns plain
# floats and strings. Pydantic converts them into proper dates and Decimals after.
class _LineItem(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float


class _GeminiInvoice(BaseModel):
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    line_items: list[_LineItem] = Field(default_factory=list)


def extract_invoice(file_path: str) -> ExtractedInvoice:
    path = Path(file_path)
    media_type = MEDIA_TYPES[path.suffix.lower()]

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Part.from_bytes(data=path.read_bytes(), mime_type=media_type),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GeminiInvoice,
            temperature=0,
        ),
    )

    raw = _GeminiInvoice.model_validate_json(response.text)
    return ExtractedInvoice.model_validate(raw.model_dump())
