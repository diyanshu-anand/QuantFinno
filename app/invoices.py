from datetime import datetime

def generate_invoice_number(db):
    now = datetime.now()
    prefix = f"INV-{now.strftime('%Y%m')}"

    count = db.execute(
        f"SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE '{prefix}%"
    ).scalar()

    return f"{prefix}-{str(count +1).zfill(4)}"