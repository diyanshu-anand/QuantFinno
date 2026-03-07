from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Customer
from app.schemas import CustomerCreate, CustomerResponse, CustomerLogin

router = APIRouter(prefix="/customers", tags=["Customers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CustomerResponse)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db)
):
    customer = Customer(
        name=payload.name,
        phone=payload.phone
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.get("/")
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers


# @router.post("/login", response_model=CustomerResponse)
# def login_customer(mobile: str, db: Session = Depends(get_db)):
#     customer = db.query(Customer).filter(Customer.phone == mobile).first()
#     if not customer:
#         raise HTTPException(status_code=404, detail="Customer not found")
#     return customer


@router.post("/login", response_model=CustomerResponse)
def login_customer(payload: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.phone == payload.mobile).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
