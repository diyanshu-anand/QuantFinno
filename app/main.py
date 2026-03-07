from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, crud
from .models import Transaction
from app.routers import transactions
from app.routers import customers
from app.routers import reports
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(transactions.router)
app.include_router(customers.router)
app.include_router(reports.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/customers")
def add_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    obj = models.Customer(**customer.dict())
    db.add(obj)
    db.commit()
    return obj


@app.post("/transactions")
def add_transaction(txn: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, txn)



