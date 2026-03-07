# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from datetime import date
# from app.database import SessionLocal
# from app.models import Transaction
# from app.utils.invoice import generate_invoice_id

# router = APIRouter(prefix="/transactions", tags=["Transactions"])

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/")
# def create_transaction(
#     customer_id: str,
#     transaction_date: date,
#     amount_due: float,
#     amount_paid: float,
#     payment_mode: str,
#     description: str = None,
#     db: Session = Depends(get_db)
# ):
#     seq = db.query(Transaction).count() + 1
#     invoice_id = generate_invoice_id(seq)

#     txn = Transaction(
#         customer_id=customer_id,
#         transaction_date=transaction_date,
#         amount_due=amount_due,
#         amount_paid=amount_paid,
#         payment_mode=payment_mode,
#         description=description,
#         invoice_id=invoice_id
#     )

#     db.add(txn)
#     db.commit()
#     db.refresh(txn)

#     return {
#         "message": "Transaction created",
#         "invoice": invoice_id,
#         "outstanding": amount_due - amount_paid
#     }


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from uuid import UUID
from app.database import SessionLocal
from app.models import Transaction, Customer
from sqlalchemy import func

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_transaction(
    customer_id: UUID,
    transaction_date: date,
    amount_due: float,
    amount_paid: float,
    payment_mode: str,
    particulars: str,
    db: Session = Depends(get_db)
):
    # Fetch customer name
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    txn = Transaction(
        customer_id=customer_id,
        date=transaction_date,
        amount_due=amount_due,
        amount_paid=amount_paid,
        payment_mode=payment_mode,
        note=particulars
    )

    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {
        # "message": "Transaction created successfully",
        "index": str(txn.id),

        # HUMAN READABLE
        "customer_name": customer.name,

        # TRANSACTION DETAILS
        "transaction_date": txn.date,
        "payment_mode": txn.payment_mode,
        "amount_due": float(txn.amount_due),
        "amount_paid": float(txn.amount_paid),
        "particulars": txn.note,

        # DERIVED
        "outstanding_amount": float(txn.amount_due - txn.amount_paid)
    }


@router.get("/export")
def export_transactions(db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction, Customer)
        .join(Customer, Transaction.customer_id == Customer.id)
        .all()
    )

    result = []

    for txn, customer in transactions:
        result.append({
            "transaction_id": str(txn.id),
            "customer_name": customer.name,
            "transaction_date": txn.date.isoformat(),
            "payment_mode": txn.payment_mode,
            "amount_due": float(txn.amount_due),
            "amount_paid": float(txn.amount_paid),
            "particulars": txn.note,
            "outstanding_amount": float(txn.amount_due - txn.amount_paid)
        })

    return {
        "count": len(result),
        "transactions": result
    }


@router.get("/vendor/{customer_id}")
def get_vendor_transactions(customer_id: UUID, db: Session = Depends(get_db)):

    txns = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.date.desc())
        .all()
    )

    result = []

    for txn in txns:
        result.append({
            "id": str(txn.id),
            "date": txn.date,
            "amount_due": float(txn.amount_due),
            "amount_paid": float(txn.amount_paid),
            "payment_mode": txn.payment_mode,
            "particulars": txn.note,
            "balance": float(txn.amount_due - txn.amount_paid)
        })

    return result


@router.get("/dues")
def get_vendor_dues(db: Session = Depends(get_db)):

    results = (
        db.query(
            Customer.id,
            Customer.name,
            func.sum(Transaction.amount_due - Transaction.amount_paid).label("total_due")
        )
        .join(Transaction, Customer.id == Transaction.customer_id)
        .group_by(Customer.id)
        .all()
    )

    data = []

    for r in results:
        data.append({
            "customer_id": str(r.id),
            "customer_name": r.name,
            "total_due": float(r.total_due)
        })

    return data