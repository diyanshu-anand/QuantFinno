import os
import qrcode
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
# (Optional later) from app.models import RentTransaction
from datetime import datetime, timedelta
from app.models import Rent

def cleanup_old_rent(db):
    cutoff_date = datetime.utcnow() - timedelta(days=60)

    db.query(Rent).filter(Rent.created_at < cutoff_date).delete()
    db.commit()

router = APIRouter(prefix="/rent", tags=["Rent"])

UPI_ID = "7903885646-3@ybl"
NAME = "Mona Anand"

# 🔹 DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Core QR Generator (Clean function)
def generate_rent_qr(amount=3000, location="NayaRaipur"):
    txn_id = str(uuid.uuid4())[:8]

    note = f"Rent_{location}_{datetime.now().strftime('%b_%Y')}_{txn_id}"

    upi_link = (
        f"upi://pay?pa={UPI_ID}"
        f"&pn={NAME}"
        f"&am={amount}"
        f"&tn={note}"
        f"&tr={txn_id}"
    )

    # Ensure static folder exists
    os.makedirs("static", exist_ok=True)

    file_path = f"app/static/qr_{txn_id}.png"

    img = qrcode.make(upi_link)
    img.save(file_path)

    return {
        # 1. "qr_path": file_path,  # It makes the url like this http://127.0.0.1:8000/app/static/qr_xxx.png  because i have this in main.py app.mount("/static", StaticFiles(directory="app/static"), name="static") That means:

        # 2. /static/... → maps to app/static/...

        # 3. NOT:

        # 4. /app/static/...

        "qr_path": f"static/qr_{txn_id}.png", #FIXED
        "txn_id": txn_id,
        "note": note,
        "upi_link": upi_link  #  useful for debugging or future mobile use so keeping it, don't know why
    }


#  API Endpoint
@router.get("/qr")
def get_rent_qr(request: Request, db: Session = Depends(get_db)):

    #  CLEAN OLD DATA FIRST
    cleanup_old_rent(db)

    qr_data = generate_rent_qr()

    base_url = str(request.base_url).rstrip("/")

    rent_entry = Rent(
        txn_id=qr_data["txn_id"],
        note=qr_data["note"],
        amount=9000,
        status="pending",
        location="NayaRaipur"
    )

    db.add(rent_entry)
    db.commit()

    return {
        "qr_url": f"{base_url}/{qr_data['qr_path']}",
        "txn_id": qr_data["txn_id"],
        "note": qr_data["note"]
    }

@router.get("/status")
def get_rent_status(db: Session = Depends(get_db)):
    rent = (
        db.query(Rent)
        .order_by(Rent.created_at.desc())
        .first()
    )

    if not rent:
        return {"message": "No rent data"}

    return {
        "location": rent.location,
        "amount": rent.amount,
        "status": rent.status,
        "created_at": rent.created_at,
        "confirmed_at": rent.confirmed_at
    }