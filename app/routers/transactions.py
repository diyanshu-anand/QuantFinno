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
