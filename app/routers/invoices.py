import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.config import settings
from app.db import get_db
from app.processing import process_invoice
from app.schemas import InvoiceCreate, InvoiceRead

router = APIRouter(prefix="/invoices", tags=["invoices"])

ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


@router.post("/upload", response_model=InvoiceRead, status_code=202)
def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            400, f"Unsupported file type. Allowed: {sorted(ALLOWED_SUFFIXES)}"
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(exist_ok=True)
    dest = upload_dir / f"{uuid4().hex}{suffix}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    invoice = models.Invoice(file_path=str(dest), status="pending")
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    background_tasks.add_task(process_invoice, invoice.id)
    return invoice


@router.post("", response_model=InvoiceRead, status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    invoice = models.Invoice(
        **payload.model_dump(exclude={"line_items"}),
        line_items=[models.LineItem(**li.model_dump()) for li in payload.line_items],
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("", response_model=list[InvoiceRead])
def list_invoices(
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    stmt = select(models.Invoice).options(selectinload(models.Invoice.line_items))
    if status:
        stmt = stmt.where(models.Invoice.status == status)
    stmt = stmt.order_by(models.Invoice.id.desc()).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.get(models.Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
