from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers import invoices

app = FastAPI(title="Invoice Agent")
app.include_router(invoices.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
