from datetime import datetime

def generate_invoice_id(seq: int):
    date_part = datetime.now().strftime("%Y%m")
    return f"INV-{date_part}-{seq:04d}"
