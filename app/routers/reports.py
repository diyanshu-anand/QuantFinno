from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from calendar import monthrange

from app.database import SessionLocal
from app.models import Transaction, Customer

router = APIRouter(prefix="/reports", tags=["Reports"])


# -------------------- DB Dependency --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Helpers --------------------
def get_month_range(year: int, month: int):
    last_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def serialize_transaction(txn: Transaction, customer_name: str):
    outstanding = float(txn.amount_due - txn.amount_paid)

    return {
        "transaction_id": str(txn.id),
        "customer_name": customer_name,
        "transaction_date": txn.date.isoformat(),
        "payment_mode": txn.payment_mode,
        "particulars": txn.note,
        "amount_due": float(txn.amount_due),
        "amount_paid": float(txn.amount_paid),
        "outstanding_after_txn": outstanding
    }


# -------------------- CASHFLOW REPORT --------------------
@router.get("/cashflow")
def monthly_cashflow(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    start_date, end_date = get_month_range(year, month)

    transactions = (
        db.query(Transaction, Customer.name)
        .join(Customer, Customer.id == Transaction.customer_id)
        .filter(Transaction.date.between(start_date, end_date))
        .all()
    )

    total_due = 0
    total_paid = 0
    result = []

    for txn, customer_name in transactions:
        total_due += float(txn.amount_due)
        total_paid += float(txn.amount_paid)
        result.append(serialize_transaction(txn, customer_name))

    return {
        "month": f"{month}-{year}",
        "summary": {
            "total_due": total_due,
            "total_paid": total_paid,
            "total_outstanding": total_due - total_paid
        },
        "transactions": result
    }


# -------------------- CUSTOMER STATEMENT --------------------
@router.get("/customer/{customer_id}")
def customer_statement(
    customer_id: str,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    start_date, end_date = get_month_range(year, month)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return {"error": "Customer not found"}

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.customer_id == customer_id,
            Transaction.date.between(start_date, end_date)
        )
        .order_by(Transaction.date)
        .all()
    )

    txns_json = []
    total_due = 0
    total_paid = 0

    for txn in transactions:
        total_due += float(txn.amount_due)
        total_paid += float(txn.amount_paid)
        txns_json.append(serialize_transaction(txn, customer.name))

    return {
        "customer_name": customer.name,
        "month": f"{month}-{year}",
        "opening_balance": 0,  # future extension
        "transactions": txns_json,
        "closing_balance": total_due - total_paid
    }

# Accounting logic may be wrong will verify it through studies