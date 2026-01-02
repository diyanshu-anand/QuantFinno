from .models import Customer, Transaction, Invoice
from .invoices import generate_invoice_number


def create_transaction(db, data):
    txn = Transaction(**data.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)

    if data.amount_paid > 0:
        invoice = Invoice(
            transaction_id = txn.id,
            invoice_number = generate_invoice_number(db)
        )
        db.add(invoice)
        db.commit()
    return txn