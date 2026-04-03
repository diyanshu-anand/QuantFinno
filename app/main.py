# Mistakes in the code
# 1. CORSMiddleware added twice
# 2. rent router not imported → will crash
# 3. No static file serving (QR won’t load)
# 4. Duplicate imports
# 5. CORS config conflicting

# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session
# from .database import SessionLocal, engine
# from . import models, schemas, crud
# from .models import Transaction
# from app.routers import transactions
# from app.routers import customers
# from app.routers import reports
# from fastapi.middleware.cors import CORSMiddleware



# from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Finance Backend")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # OK for now
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# app.include_router(transactions.router)
# app.include_router(customers.router)
# app.include_router(reports.router)
# app.include_router(rent)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://localhost:5174",
#         "http://localhost:5175",
#         "https://quantfinno.onrender.com"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # @app.post("/customers")
# # def add_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
# #     obj = models.Customer(**customer.dict())
# #     db.add(obj)
# #     db.commit()
# #     return obj


# # @app.post("/transactions")
# # def add_transaction(txn: schemas.TransactionCreate, db: Session = Depends(get_db)):
# #     return crud.create_transaction(db, txn)




# New code with rental features
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import models

# Routers
from app.routers import transactions
from app.routers import customers
from app.routers import reports
from app.routers import rent_qr  #  IMPORTANT (new rent router)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Backend")


#  CORS (single clean config)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://quantfinno.onrender.com"
        "https://quant-finno-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#  Static Files (FOR QR IMAGES) #FIXED
app.mount("/static", StaticFiles(directory="app/static"), name="static")


#  Include Routers
app.include_router(transactions.router)
app.include_router(customers.router)
app.include_router(reports.router)
app.include_router(rent_qr.router)   #  FIXED


#  DB Dependency (keep if needed elsewhere)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()