from app import models
from app.agents.extractor import extract_invoice
from app.db import SessionLocal


def process_invoice(invoice_id: int) -> None:
    """Runs in the background after upload, with its own DB session."""
    db = SessionLocal()
    try:
        invoice = db.get(models.Invoice, invoice_id)
        invoice.status = "processing"
        db.commit()

        extracted = extract_invoice(invoice.file_path)

        invoice.vendor = extracted.vendor
        invoice.invoice_number = extracted.invoice_number
        invoice.invoice_date = extracted.invoice_date
        invoice.total = extracted.total
        invoice.currency = extracted.currency or "USD"
        invoice.line_items = [
            models.LineItem(**li.model_dump()) for li in extracted.line_items
        ]
        invoice.status = "extracted"
        db.commit()
    except Exception as exc:
        db.rollback()
        invoice = db.get(models.Invoice, invoice_id)
        invoice.status = "failed"
        invoice.review_notes = str(exc)[:500]
        db.commit()
    finally:
        db.close()
